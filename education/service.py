from django.db.models import Q, Prefetch

from education.models import Theme, Lesson, Course, TestTask, ExerciseTask
from user.models import UserCourse, UserLesson


def calculate_course_rate(course):
    rates = UserCourse.objects.filter(~Q(rating=None), course=course).values_list('rating', flat=True)
    try:
        return sum(rates) / len(rates)
    except ZeroDivisionError:
        return 0


def annotate_themes(user, pk):
    themes = Theme.objects.prefetch_related(Prefetch('lessons', Lesson.objects.filter(is_published=True))) \
        .filter(course=pk, is_published=True)
    for theme in themes:
        for lesson in theme.lessons.all():
            lesson.is_done = check_if_lesson_is_done(lesson, user)
            lesson.is_auto_done = False if lesson.tasks.all() else True
    return themes


def check_if_lesson_is_done(lesson, user):
    try:
        user_lesson = UserLesson.objects.get(lesson=lesson, user=user)
        return user_lesson.is_done
    except UserLesson.DoesNotExist:
        return False


def annotate_courses(user):
    courses = Course.objects.prefetch_related('categories').filter(usercourse__user=user)
    for course in courses:
        lesson_num = Lesson.objects.filter(theme__course=course).count()
        if lesson_num == 0:
            course.percents = 0
        else:
            course.percents = int((Lesson.objects.filter(users=user, theme__course=course,
                                                         userlesson__is_done=True).count() / lesson_num) * 100)
    return courses


def count_exercise_percents(tasks, user_lesson):
    try:
        return float(count_right_answers(tasks) / user_lesson.lesson.tasks.count()) * 100
    except ZeroDivisionError:
        return 0


def count_right_answers(tests):
    answers = 0
    for test in tests.get('tests', None):
        if [option.id for option in TestTask.objects.get(pk=test.get('id', None)).options.filter(is_true=True)] == \
                list(map(int, test.get('answers', None))):
            answers += 1
    for exercise in tests.get('exercises', None):
        if ExerciseTask.objects.get(pk=exercise.get('id', None)).answer == exercise.get('answer', None):
            answers += 1
    return answers
