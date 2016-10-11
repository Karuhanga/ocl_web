"""
Create test user.

Run this once before running e2e tests
"""
from optparse import make_option

from django.core.management import BaseCommand
from libs.ocl import OclApi

class FakeRequest(object):
    """ FakeRequest class """
    def __init__(self):
        self.session = {}

class Command(BaseCommand):
    """ manage.py Command 'create_sysadmin' """
    help = 'Create test user'
    option_list = BaseCommand.option_list + (

        make_option('--username',
                    action='store',
                    dest='username',
                    default='test',
                    help='Username to be created'),
        make_option('--password',
                    action='store',
                    dest='password',
                    default='test123',
                    help='Password'),
        make_option('--company_name',
                    action='store',
                    dest='company_name',
                    default='Open Concept Lab',
                    help='Company full name'),
        make_option('--location',
                    action='store',
                    dest='location',
                    default='Boston, MA, USA',
                    help='Location, e.g. Boston, MA, USA'),
    )

    def __init__(self):
        super(Command, self).__init__()

    def create_test_user(self):
        """ Creates the OCL sysadmin user """
        from users.models import User
        from allauth.account.models import EmailAddress

        print '==================================='


        print 'Creating Test User'

        if User.objects.filter(username=self.username).count() > 0:
            test_user = User.objects.get(username=self.username)
        else:
            test_user = User.objects.create_user(username=self.username)
        test_user.email = self.username + '@example.com'
        test_user.set_password(self.password)
        test_user.first_name = 'Test'
        test_user.last_name = 'User'
        test_user.save()

        print test_user

        if EmailAddress.objects.filter(user=test_user).count() > 0:
            email = EmailAddress.objects.get(user=test_user)

        else:
            email = EmailAddress.objects.create(user=test_user)

        email.email = test_user.email
        email.verified = True
        email.save()

        ocl = OclApi(admin=True)

        data = {
            "username": test_user.username,
            "name": test_user.first_name + ' ' + test_user.last_name,
            "email": test_user.email,
            'hashed_password': test_user.password,
            "company": self.company_name,
            "location": self.location,
            "preferred_locale": 'en'
        }



        result = ocl.create_user(data)
        print 'Test User Submitted to API: username=' + self.username + ', password=' + self.password + ', status_code=' + str(result.status_code)

        if result.status_code == 201:
            print '==================================='
        elif result.status_code == 400:
            # try reactivate for now, this is very not secure, #TODO
            result = ocl.reactivate_user(test_user.username)
            if result == 204:
                print 'reactivated'
                print '==================================='
        else:
            exit(1)

    def handle(self, *args, **options):

        self.location = options['location']
        self.company_name = options['company_name']
        self.username = options['username']
        self.password = options['password']


        self.create_test_user()
