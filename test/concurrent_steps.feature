Feature: Concurrent steps

    Test concurrent steps
    
    @parallell
    Scenario: multiple concurrent steps interleaved
        Then step1
        Concurrently step2
        Then step1
        Concurrently step2
    
    @parallell
    Scenario: multiple concurrent steps only
        Concurrently step2
        (background) Then step2
        (background) When step2
    
    @concurrent
    Scenario: mixed concurrent steps
        Concurrently step2
        Concurrently step2
        Then step1
        Then step1
        Concurrently step2
    
    Scenario: sequential steps only
        Then step1
        Then step1
    