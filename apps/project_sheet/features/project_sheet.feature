Feature: Editing a project sheet
  To edit a project sheet and its translations.

  Scenario: Create a new project sheet
    Given I navigate to "/project/add/"
    Then I should see the message "Want to get started on your project sheet ?"

  Scenario: Editing tags
    Given I want to change the themes of my project
    When I tag it with "banana, postit"
    Then My project is at least tagged with "banana, postit"

  Scenario: Editing project status as a logged in user
    Given I am a logged in user
    And the project status is "IDEA"
    When I change the status of a project to "END"
    Then the project status is "END"

  Scenario: Editing project status without being logged in
    Given I am not a logged in user
    And the project status is "IDEA"
    When I change the status of a project to "END"
    Then the project status is "IDEA"
