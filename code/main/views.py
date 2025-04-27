from django.shortcuts import render, HttpResponse
from django.http.response import JsonResponse
from django.db.models import Count, Avg, Max, Min
from django.core import serializers


from main.models import Course, CourseContent, CourseMember, Comment, User

def index(request):
    return HttpResponse("<h1>selamat datang</h1>")

def testing(request):
    guru = User.objects.create_user(
        username="guru1",
        email="guru1@gmail.com",
        password="guru1123",
        first_name="Guru",
        last_name="satu"
    )
       
    Course.objects.create(
        name="Pemorograman Python",
        description="bedalajr python dek",
        price=300000,
        teacher = guru
    )

    return HttpResponse("kosongan")

def allCourse(request):
    allCourse = Course.objects.all()
    result = []
    for course in allCourse:
        record = {'id': course.id, 'name': course.name, 
                  'description': course.description, 
                  'price': course.price,
                  'teacher': {
                      'id': course.teacher.id,
                      'username': course.teacher.username,
                      'email': course.teacher.email,
                      'fullname': f"{course.teacher.first_name} {course.teacher.last_name}"
                  }}
        result.append(record)
    return JsonResponse(result, safe=False)

def courseStat(request):
  courses = Course.objects.all()
  stats = courses.aggregate(max_price=Max('price'),
                              min_price=Min('price'),
                              avg_price=Avg('price'))
  cheapest = Course.objects.filter(price=stats['min_price'])
  expensive = Course.objects.filter(price=stats['max_price'])
  popular = Course.objects.annotate(member_count=Count('coursemember'))\
                          .order_by('-member_count')[:5]
  unpopular = Course.objects.annotate(member_count=Count('coursemember'))\
                          .order_by('member_count')[:5]

  result = {'course_count': len(courses), 'courses': stats,
            'cheapest': serializers.serialize('python', cheapest), 
            'expensive': serializers.serialize('python', expensive),
            'popular': serializers.serialize('python', popular), 
            'unpopular': serializers.serialize('python', unpopular)}
  return JsonResponse(result, safe=False)



def statistics_view(request):
    # 1. Jumlah user yang membuat course (sebagai teacher)
    users_with_courses = User.objects.filter(course__isnull=False).distinct().count()

    # 2. Jumlah user yang tidak memiliki course
    users_without_courses = User.objects.filter(course__isnull=True).count()

    # 3. Rata-rata jumlah course yang diikuti per user
    avg_courses_per_user = CourseMember.objects.values('user_id').annotate(total=Count('course_id')).aggregate(avg=Avg('total'))['avg']

    # 4. User yang mengikuti course terbanyak
    most_active_member = CourseMember.objects.values('user_id').annotate(total=Count('course_id')).order_by('-total').first()
    user_with_most_courses = None
    if most_active_member:
        user_with_most_courses = User.objects.get(id=most_active_member['user_id'])

    # 5. List user yang tidak mengikuti course sama sekali
    users_without_subscriptions = User.objects.filter(coursemember__isnull=True)

    context = {
        "users_with_courses": users_with_courses,
        "users_without_courses": users_without_courses,
        "avg_courses_per_user": avg_courses_per_user,
        "user_with_most_courses": user_with_most_courses,
        "users_without_subscriptions": users_without_subscriptions,
    }
    return render(request, "statistics.html", context)
        
    
