Feature: Dependency feature

    @id_1
    @group_first
    Scenario: scenario 1
        Then step 1
    
    @depends_1
    Scenario: scenario 2
        Then step 1
    
    @dependsGroups_first
    Scenario: scenario 3
        Then step 1