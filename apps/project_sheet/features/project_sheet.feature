Feature: Editing a project sheet

    Scenario: Editing tags
        Given I want to change the themes of my project
	When I tag it with "banana, postit"
        Then My project is at least tagged with "banana, postit"
