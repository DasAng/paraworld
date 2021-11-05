Feature: I/O test with multiple threads

    Test running network I/O request with multiple threads

    @concurrent
    Scenario: Call a slow API
        Then call api
    
    @concurrent
    Scenario: Call a slow API 2
        Then call api