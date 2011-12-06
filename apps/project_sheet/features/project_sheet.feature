Feature: Editing a project sheet
  To edit a project sheet and its translations.

  Scenario: Create a new project sheet
    Given I navigate to "/project/add/"
    Then I should see the message "Want to get started on your project sheet ?"

  Scenario: Editing tags
    Given I want to change the themes of my project
    When I tag it with "banana, postit"
    Then My project is at least tagged with "banana, postit"
