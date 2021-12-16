Feature: Test parallel world

    Test that world objects gets shared between parallel process

    @parallel
    @id_scenario1
    Scenario: scenario 1
        Then step 1
    
    @parallel
    Scenario: scenario 2
        Then step 2