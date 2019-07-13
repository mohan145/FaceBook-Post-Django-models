import pytest
from postv1.models import User


@pytest.mark.django_db
def test_my_user():
    User.objects.create(name='kmk', profile_pic_url='kmk@xyz.com')
    User.objects.create(name='kmk', profile_pic_url='kmk@xyz.com')

    with pytest.raises(Exception) as e:
        User.objects.get(name="kmk")
    assert "Multiple" in str(e)



@pytest.mark.django_db
def test_my_user_count():
    User.objects.create(name='kmk', profile_pic_url='kmk@xyz.com')
    User.objects.create(name='kmk', profile_pic_url='kmk@xyz.com')

    c = User.objects.count()
    assert c == 2
