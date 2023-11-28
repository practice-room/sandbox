Feature: showing off behave

 Scenario Outline: [HC-00-000] Run a simple test
    Given we have behave installed
     When we implement a test
     Then behave will test it for us with <thing>!
 
 @tutorial
 Examples: Amphibians
   | thing         |
   | Red Tree Frog |
