Feature: Spotlit_due_diligence

  Scenario: Admin report selection
    Given The user is logged into Django Admin
    When The user goes to a companies dashboard
    Then The user should be able to select individual report types
    And The user should be able to select corporate report types

  Scenario: Archived Report Template Name
    Given The admin has selected an individual report type
    When The manager views archived reports
    Then The request should have a report template type

  Scenario: Archiving Reports
    Given The test employee logs into Django Admin and creates a request
    And The manager logs into Django Admin and assigns the request to analyst1
    And The analyst1 logs into Django Admin and completes request
    When The manager completes the request and accesses the Archived reports menu
    And The manager accesses the Archived reports menu
    Then The request should have been archived

