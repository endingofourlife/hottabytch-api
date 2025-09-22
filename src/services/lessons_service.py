import json
import uuid
from datetime import datetime, timezone
from typing import Optional

from redis.asyncio import Redis

from src.database.models import LessonModel
from src.repository import LessonsRepository
from src.schemas.tests_schemas import StartLessonRequest, StartLessonResponse, CheckLessonAnswerRequest, \
    CheckLessonAnswerResponse, LessonResultResponse, LessonCreateRequest, CreateLessonResponse, \
    SimplifiedLessonResponse, ActualLessonResponse
from src.services import ServiceResult
from src.services.mappers import LessonsMapper


class LessonsService:
    def __init__(self, repository: LessonsRepository, redis_client: Redis):
        self._repository = repository
        self._redis_client = redis_client
        self.lesson_cache_ttl = 864000  # 10 days
        self.session_ttl = 1800 # 30 minutes

    def _calculate_xp(self, success_percent: int) -> int:
        base_xp = 100

        if success_percent == 100:
            return base_xp * 2
        elif success_percent >= 80:
            return base_xp
        elif success_percent >= 50:
            return base_xp // 2
        else:
            return 10

    def _get_correct_answers(self, lesson: LessonModel) -> dict[int, int]:
        print(f"Getting correct answers for lesson: {lesson.lesson_id}. Questions count: {len(lesson.questions)}\n"
              f"Questions: {[q.question_id for q in lesson.questions]}. Correct answer: {[q.answers[0].answer_id for q in lesson.questions if q.answers]}")
        return {
            question.question_id: next((a.answer_id for a in question.answers if a.is_correct), None)
            for question in lesson.questions
        }

    async def _get_cached_lesson(self, lesson_id: int) -> Optional[dict]:
        key = f"lesson:{lesson_id}:data"
        try:
            cached_data = await self._redis_client.get(key)
            return json.loads(cached_data) if cached_data else None
        except json.JSONDecodeError:
            return None

    async def _cache_lesson(self, lesson_id: int, lesson: LessonModel):
        correct_answers = self._get_correct_answers(lesson)
        print(f'Cache lesson. Got correct answers: {correct_answers}')
        lesson_data = LessonsMapper.to_lesson_cache(lesson, correct_answers)
        print(f'Caching lesson data: {lesson_data}')
        await self._redis_client.set(
            f"lesson:{lesson_id}:data",
            json.dumps(lesson_data),
            ex=self.lesson_cache_ttl
        )

    async def _create_user_session(self, session_id: str, request: StartLessonRequest, correct_answers: dict[int,int]):
        """
        Session data will be stored in Redis and gotten each time the user checks an answer.
        """
        session_data = {
            'user_id': request.user_id,
            'lesson_id': request.lesson_id,
            'started_at': datetime.now().isoformat(),
            'correct_answers': correct_answers,
            'user_answers': [],
            'wrong_answered': [],
        }
        await self._redis_client.set(
            f"session:{session_id}",
            json.dumps(session_data),
            ex=self.session_ttl
        )

    async def start_lesson(self, request: StartLessonRequest):
        """
        Method starts a lesson and creates a user session based on his id and lesson id.
        It first checks if the lesson is cached. If it is, it returns the cached data.
        If not, it fetches the lesson from the database, caches it, and returns the lesson data.
        """
        try:
            session_id = f"{request.lesson_id}{request.user_id}"
            cached_data = await self._get_cached_lesson(request.lesson_id)
            if cached_data:
                response = LessonsMapper.to_start_lesson_response_cache(
                    session_id=session_id,
                    questions=cached_data.get('questions')
                )
                await self._create_user_session(session_id, request, cached_data.get('correct_answers'))
                return ServiceResult.success(response)

            lesson = await self._repository.get_lesson_by_id(request.lesson_id)
            if not lesson:
                return ServiceResult.failure('Lesson not found', status_code=404)

            await self._cache_lesson(lesson.lesson_id, lesson)
            correct_answers = self._get_correct_answers(lesson)
            await self._create_user_session(session_id, request, correct_answers)

            return ServiceResult.success(
                LessonsMapper.to_start_lesson_response(
                    session_id=session_id,
                    lesson=lesson
                )
            )
        except Exception as e:
            return ServiceResult.failure(f'Error starting lesson: {str(e)}', status_code=500)

    async def check_lesson_answer(self, request: CheckLessonAnswerRequest) -> ServiceResult[CheckLessonAnswerResponse]:
        """
        Method checks the answer via cached session data. If the session is not found or expired,
        it returns an error. If the answer is correct, it updates the session data.
        The session TTL will be set to 30min after each answer check.
        """
        try:
            session = await self._redis_client.get(f'session:{request.session_id}')
            if not session:
                return ServiceResult.failure('Session not found or expired', status_code=404)

            session_data = json.loads(session)

            # check if time is expired
            started_at = datetime.fromisoformat(session_data.get('started_at')).replace(tzinfo=timezone.utc)
            if (datetime.now(timezone.utc) - started_at).total_seconds() > 1800:  # 30 min for a test
                await self._redis_client.delete(f'session:{request.session_id}')
                return ServiceResult.failure('Test time has expired', status_code=403)

            correct_answer_id = session_data.get('correct_answers').get(str(request.question_id))
            is_correct = correct_answer_id == request.answer_id
            print(f"User answer: {request.answer_id} Question: {request.question_id} Correct answer: {correct_answer_id} Is correct: {is_correct}")
            if is_correct:
                session_data['user_answers'].append(request.question_id)
            else:
                session_data['wrong_answered'].append(request.question_id)

            await self._redis_client.set(
                f'session:{request.session_id}',
                json.dumps(session_data),
                ex=self.session_ttl
            )

            if len(session_data.get('user_answers')) == len(session_data.get('correct_answers')):
                await self.save_lesson_results(request.session_id)

            return ServiceResult.success(
                LessonsMapper.to_answer_check_response(
                    question_id=request.question_id,
                    is_correct=is_correct
                )
            )
        except json.JSONDecodeError:
            return ServiceResult.failure('Invalid session data', status_code=400)

    async def save_lesson_results(self, session_id: str) -> None:
        try:
            session = await self._redis_client.get(f'session:{session_id}')
            if not session:
                return ServiceResult.failure('Session not found or expired', status_code=404)

            session_data = json.loads(session)

            total_questions = len(session_data.get('correct_answers'))
            if len(session_data.get('user_answers')) < total_questions:
                return ServiceResult.failure('Test not completed', status_code=400)

            incorrect_count = len(session_data.get('wrong_answered'))
            success_percent = min(100, int(((total_questions - incorrect_count) / total_questions) * 100))
            xp_earned = self._calculate_xp(success_percent)
            progress = await self._repository.save_user_progress(
                user_id=session_data.get('user_id'),
                lesson_id=session_data.get('lesson_id'),
                xp_earned=xp_earned,
                success_percent=success_percent
            )
            if not progress:
                raise ValueError('Failed to save user progress')
            await self._redis_client.set(
                f'lesson_result:{session_id}',
                json.dumps({
                    'xp_earned': xp_earned,
                    'success_percent': success_percent,
                }),
                ex=self.session_ttl
            )
            await self._redis_client.delete(f'session:{session_id}')

        except Exception as e:
            raise ValueError(f'Error saving lesson results: {str(e)}')

    async def get_lesson_result(self, session_id: str) -> ServiceResult[LessonResultResponse]:
        cached = await self._redis_client.get(f'lesson_result:{session_id}')
        if not cached:
            return ServiceResult.failure('Lesson result not found or expired', status_code=404)
        data = json.loads(cached)
        return ServiceResult.success(
            LessonsMapper.to_lesson_result_response(
                xp_earned=data.get('xp_earned'),
                success_percent=data.get('success_percent'),
            )
        )

    async def create_lesson(self, request: LessonCreateRequest) -> ServiceResult[CreateLessonResponse]:
        try:
            new_test = await self._repository.create_lesson(
                title=request.title,
                description=request.description,
                language_id=request.language_id
            )
            if not new_test:
                return ServiceResult.failure('Failed to create test', status_code=400)
            response = LessonsMapper.to_create_lesson_response(lesson=new_test)
            return ServiceResult.success(response)
        except Exception as e:
            return ServiceResult.failure(f'Error creating test: {str(e)}', status_code=500)

    async def get_all_lessons(self) -> ServiceResult[list[SimplifiedLessonResponse]]:
        try:
            lessons = await self._repository.get_all_lessons()
            if not lessons:
                return ServiceResult.success([])
            response = LessonsMapper.to_all_lessons_response(lessons)
            return ServiceResult.success(response)
        except Exception as e:
            return ServiceResult.failure(f'Error fetching tests: {str(e)}', status_code=500)

    async def get_actual_lesson(self, user_id: int) -> ServiceResult[Optional[ActualLessonResponse]]:
        try:
            user_cache_key = f'user:{user_id}'
            cached_data = await self._redis_client.get(user_cache_key)
            if cached_data:
                cached_data = json.loads(cached_data)
                if cached_data.get('is_streak', False):
                    return ServiceResult.failure('User is in streak mode, no unfinished lesson available', status_code=403)
                else:
                    lesson = await self._repository.get_unfinished_lesson_with_tests(user_id)
            else:
                lesson = await self._repository.get_unfinished_lesson_with_tests(user_id, True)
            if not lesson:
                return ServiceResult.failure('No unfinished lesson found', status_code=404)
            return ServiceResult.success(
                ActualLessonResponse(
                    lesson_id=lesson.lesson_id,
                    title=lesson.title,
                    description=lesson.description
                )
            )
        except Exception as e:
            return ServiceResult.failure(f'Error fetching actual lesson: {str(e)}', status_code=500)