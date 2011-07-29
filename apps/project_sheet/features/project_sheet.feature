Feature: Editing a project sheet
  To edit a project sheet and its translations.

  Scenario: Create a new project sheet
    Given I navigate to the home page
    When I click on the "Add a project" link
    Then I should see the message "Want to get started on your project sheet ?"
