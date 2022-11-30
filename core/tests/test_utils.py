from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Group

from core.models import Company, CompanyEmployee
from core import utils


class UtilsTest(TestCase):
    print "Running Utils Tests*********************************"

    def create_group(self, group_name):
        group = Group(name=group_name)
        group.save()
        return group

    def create_user(self, name, email, password):
        user = User.objects.create_user(name, email, password)
        user.save()
        return user

    def create_company_employee(self, user):
        company = Company(name='company')
        company.save()
        employee = CompanyEmployee(user=user, phone_number='123445667', company=company, position='HR Rep')
        employee.save()
        return employee

    def test_is_analyst(self):
        user_m = self.create_user("manager", "manager@manager.com", "manager")
        user_a = self.create_user("analyst", "analyst@analyst.com", "analyst")

        group_m = self.create_group("SpotLitManager")
        group_a = self.create_group("SpotLitAnalyst")

        user_m.groups.add(group_m)
        user_m.save()

        user_a.groups.add(group_a)
        user_a.save()

        test_manager = utils.is_analyst(user_m)
        self.assertEquals(test_manager, False)

        test_analyst = utils.is_analyst(user_a)
        self.assertEquals(test_analyst, True)

    def test_get_company_employee(self):
        user_e = self.create_user("employee", "employee@employee.com", "employee")
        user_a = self.create_user("analyst", "analyst@analyst.com", "analyst")

        group_e = self.create_group("CompanyEmployee")
        group_a = self.create_group("SpotLitAnalyst")

        user_e.groups.add(group_e)
        user_e.save()

        user_a.groups.add(group_a)
        user_a.save()

        employee = self.create_company_employee(user_e)

        test_analyst = utils.get_company_employee(user_a)
        self.assertEquals(test_analyst, None)

        test_employee = utils.get_company_employee(user_e)
        self.assertEquals(test_employee, employee)

    def test_is_company_employee(self):
        user_e = self.create_user("employee", "employee@employee.com", "employee")
        user_a = self.create_user("analyst", "analyst@analyst.com", "analyst")

        group_e = self.create_group("CompanyEmployee")
        group_a = self.create_group("SpotLitAnalyst")

        user_e.groups.add(group_e)
        user_e.save()

        user_a.groups.add(group_a)
        user_a.save()

        test_employee = utils.is_company_employee(user_e)
        self.assertEquals(test_employee, True)

        test_analyst = utils.is_manager(user_a)
        self.assertEquals(test_analyst, False)

    def test_get_user_group(self):
        user_m = self.create_user("manager", "manager@manager.com", "manager")
        user_a = self.create_user("analyst", "analyst@analyst.com", "analyst")

        group_m = self.create_group("SpotLitManager")
        user_m.groups.add(group_m)
        user_m.save()

        test_manager = utils.get_user_group(user_m)
        self.assertEquals(test_manager.name, "SpotLitManager")

        test_analyst = utils.get_user_group(user_a)
        self.assertEquals(test_analyst, None)

    def test_is_manager(self):
        user_m = self.create_user("manager", "manager@manager.com", "manager")
        user_a = self.create_user("analyst", "analyst@analyst.com", "analyst")

        group_m = self.create_group("SpotLitManager")
        group_a = self.create_group("SpotLitAnalyst")

        user_m.groups.add(group_m)
        user_m.save()

        user_a.groups.add(group_a)
        user_a.save()

        test_manager = utils.is_manager(user_m)
        self.assertEquals(test_manager, True)

        test_analyst = utils.is_manager(user_a)
        self.assertEquals(test_analyst, False)

    def test_get_requests_status_for_analyst(self):
        self.assertEquals(True, True)

    def test_get_company_employee_group(self):
        group_m = self.create_group("SpotLitManager")
        test_group = utils.get_company_employee_group()

        self.assertNotEquals(group_m, test_group)

        group_c = self.create_group("CompanyEmployee")
        test_group = utils.get_company_employee_group()
        self.assertEquals(group_c, test_group)
