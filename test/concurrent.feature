Feature: Test feature

    Feature Description

    # Background: Setup
    #     Then con 1

    @parallel
    Scenario: scenario 1
        Then step 1
        Then step 2
        Concurrent con 1
        Concurrent con 2
    
    Scenario: scenario 2
        Then con 1
    
    Scenario: scenario 3
        Then con 1