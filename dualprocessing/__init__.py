from __future__ import absolute_import
from __future__ import print_function

__version__ = "0.2.2"

import multiprocessing, asyncio, logging, concurrent.futures, time, uuid, sys

class AsyncCall(object):
    """Describes a call to the pipeline.
    
    Parameters
    ----------
    targetMethod : str
        the name of the method to call (must be a method of the object returned by the function that you pass to the Broker constructor)

    *args
        Variable length argument list. (arguments of the target method)

    *kwargs
        Arbitrary keyword arguments (of the target method)
    """
    def __init__(self, targetMethod:str, *args, **kwargs):
        self.TargetMethod = targetMethod
        self.Key = str(uuid.uuid4())
        self.Args = args
        self.Kwargs = kwargs
        return

class AsyncResponse(object):
    """Describes the result of a call.
    
    Parameters
    ----------
    Key : str
        the random key used to associate AsyncCall and AsyncResponse objects

    Success : bool
        indicates if execution of the call was successful

    Result
        value returned by the target method

    Error : Exception
        exception that occurred during execution of the call
    """
    def __init__(self, key:str, success:bool, result:object, error:Exception):
        self.Key = key
        self.Success = success
        self.Result = result
        self.Error = error
        return


class Broker(object):
    """Handles scheduling and running of computations on a second process."""

    def __init__(self, processorConstructor, *pc_args, **pc_kwargs):
        """Starts a second thread for calling methods on the instance created through processorConstructor.
        
        Parameters
        ----------
        processorContructor : function
            function that returns an instance of the computation pipeline

        *pc_args
            Variable length argument list. (arguments of processor constructor)

        *pc_kwargs
            Arbitrary keyword arguments (of the processor constructor)
        """
        self.FinishedTasks = {}
        self.RunningTasks = []
        childEnd, self.__ParentEnd__ = multiprocessing.connection.Pipe()
        self.__ComputationProcess__ = multiprocessing.Process(target=self.__start__, args=(childEnd,processorConstructor, pc_args, pc_kwargs), name="ComputationProcess")
        self.__ComputationProcess__.start()
        self.ThreadExecutor = concurrent.futures.ThreadPoolExecutor(256)
        self.ThreadExecutor.submit(self.__receive__)
        return

    @classmethod
    def __start__(clsself, pipeEnd:multiprocessing.connection.Pipe, processorConstructor, pc_args, pc_kwargs):
        """Instantiates processorConstructor and executes calls on the instance of the processor.

        Listens for incoming calls through the pipe.

        Sends return values of executed calls back through the pipe.

        Parameters
        ----------
        pipeEnd : multiprocessing.connection.Pipe
            child end of the pipe connection to the broker process

        processorContructor : function
            function that returns an instance of the computation pipeline

        *pc_args
            Variable length argument list. (arguments of processor constructor)

        *pc_kwargs
            Arbitrary keyword arguments (of the processor constructor)
        """
        logging.info("Broker: process started")
        # we're now on the second process, so we can create the processor
        processor = processorConstructor(*pc_args, **pc_kwargs)
        logging.info("Broker: processor initialized")
        # endlessly loop
        while True:
            # get input key
            call, = pipeEnd.recv()
            # process input synchronously
            logging.info("{0} processing".format(call.Key))
            # execute the said method on the processor
            response = None
            try:
                returned = processor.__getattribute__(call.TargetMethod)(*call.Args, **call.Kwargs)
                response = AsyncResponse(call.Key, True, returned, None)
            except:
                response = AsyncResponse(call.Key, False, None, sys.exc_info()[1])
            pipeEnd.send((response,))
            # continue looping
        # will never return
        return

    def submit_call(self, call:AsyncCall):
        """Submits a call and returns immediately.

        Parameters
        ----------
        call : AsyncCall
            the call that is to be scheduled

        Returns
        -------
        str
            call.Key
        """
        logging.info("{0} scheduled {1}".format(call.Key, call.TargetMethod))
        # add the key to the queue
        self.__ParentEnd__.send((call,))
        self.RunningTasks.append(call.Key)
        return call.Key
    
    def submit_call_async(self, call:AsyncCall):
        """(asynchronous) Submits a call and yields the result.
        
        Parameters
        ----------
        call : AsyncCall
            the call that is to be scheduled

        Returns
        -------
        generator 
            a generatorthat yields AsyncResponse

        Examples
        --------
        @asyncio.coroutine
        def myfunc():
            call = broker.AsyncCall("uppercase", text="blabla")
            asyncResponse = yield compuBroker.submit_call_async(call)
            print(asyncResponse.Sucess)
            print(asyncResponse.Result)
            
        """
        self.submit_call(call)
        return self.get_result_async(call.Key)
    
    def get_result_async(self, key:str):
        """(asynchronous) Spawns a thread to wait for completion of a running call.
        Parameters
        ----------
        key : str
            key of the original AsyncCall

        Returns
        --------
        generator
            a generator that yields (AsyncResponse || None)

        Examples
        --------
        @asyncio.coroutine
        def myfunc():
            call = broker.AsyncCall("uppercase", text="blabla")
            compuBroker.submitCall(call)
            asyncResponse = yield compuBroker.getResultAsync(call.Key)
            print(asyncResponse.Sucess)
            print(asyncResponse.Result)
        """
        return self.ThreadExecutor.submit(self.get_result, key)

    def get_result(self, key:str):
        """(blocking) Waits until the key is not present in RunningTasks.
        Parameters
        ----------
        key : str
            key of the original AsyncCall

        Returns
        --------
        (AsyncResponse || None)
        """
        while (key in self.RunningTasks):
            time.sleep(0.05)
        if (key in self.FinishedTasks):
            return self.FinishedTasks.pop(key)
        else:
            return None

    def __receive__(self):
        """Continuously listen for tasks being completed."""
        while (True):
            time.sleep(0.005)
            # receive all computations that have finished
            while self.__ParentEnd__.poll():
                response, = self.__ParentEnd__.recv()
                self.FinishedTasks[response.Key] = response
                self.RunningTasks.remove(response.Key)
                if (not response.Success):
                    logging.warning("{0} failed: {1}".format(response.Key, response.Error))
                else:
                    logging.info("{0} completed".format(response.Key))
        return
    

    

    