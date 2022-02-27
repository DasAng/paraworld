Feature: Dependency feature

    @scenario1
    @id_1
    @group_first
    Scenario: scenario 1
        Then step 1
    
    @scenario2
    @depends_1
    Scenario: scenario 2
        Then step 1
    
    @scenario3
    @dependsGroups_first
    Scenario: scenario 3
        Then step 1
    
    @scenario4
    Scenario: scenario 4
        Then step 1