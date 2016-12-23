# Summary
This module is designed to help with running a single-instance, thread-blocking computation pipeline on a second process. It does all the heavy lifting of scheduling calls and asynchronously waiting for the results.

# Scenario
The primary use case is running of a webservice that executes blocking calls sequentially on a second process. Handlers of the webservice will remain asynchronous, therefore many requests can be accepted in parallel.
Some typical constraints include:
+ you want to accepts many requests in parallel
+ backend calls are slow (fine for the client, but unacceptable for the server)
+ backend calls are blocking
+ backend calls return picklable values
+ backend calls are first-in-first-out
+ there exists only one instance of the backend thing that is called
+ all calls must happen on the same thread/process
+ thing import and instance creation is slow (common for deep learning frameworks)

# Solution
A Broker is created that runs a user-provided constructor on a new thread to create one instance of the *Processor* (thing).

A pipe connection between the Broker (first process) and the *Processor* (second process) is used to transfer calls and their results.

Each call is indentified by a unique key. When a it comes in, it is passed through the pipe to the backend computation process. The loop at the other end of the pipe sequentially does the (blocking) calls, while the main thread asynchronously waits for the response to be returned through the pipe.

For an example of a webservice using the *dualprocessing* module, take a look [here](https://github.com/michaelosthege/tornado-compute).
