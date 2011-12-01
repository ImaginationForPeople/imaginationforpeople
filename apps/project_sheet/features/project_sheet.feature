Feature: Editing a project sheet
  To edit a project sheet and its translations.

  Scenario: Create a new project sheet
    Given I navigate to "/project/add/"
    Then I should see the message "Want to get started on your project sheet ?"
