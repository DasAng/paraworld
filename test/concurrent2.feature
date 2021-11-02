Feature: Test feature 2

    Feature Description

    # Background: Setup
    #     Then con 1

    @parallel
    Scenario: scenario 1_1
        Then step 1
        Concurrent con 1
        Concurrent con 2
    
    Scenario: scenario 2_2
        Then con 1
        Then con 1
        