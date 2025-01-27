[![AnalyticsDojo](https://github.com/rpi-techfundamentals/spring2019-materials/blob/master/fig/final-logo.png?raw=1)](http://rpi.analyticsdojo.com)
<center><h1>Introduction to Map Reduce</h1></center>
<center><h3><a href = 'http://rpi.analyticsdojo.com'>rpi.analyticsdojo.com</a></h3></center>

Adopted from work by Steve Phelps:
https://github.com/phelps-sg/python-bigdata 
This work is licensed under the Creative Commons Attribution 4.0 International license agreement.



### Overview

1. Recap of functional programming in Python
2. Python's `map` and `reduce` functions
3. Writing parallel code using `map`
4. The Map-Reduce programming model



## History

- The Map-Reduce programming model was popularised by Google (Dean and Ghemawat 2008).

- The first popular open-source implementation was Apache Hadoop, first released in 2011.


## Functional programming

Consider the following code:

def double_everything_in(data):
    result = []
    for i in data:
        result.append(2 * i)
    return result

def quadruple_everything_in(data):
    result = []
    for i in data:
        result.append(4 * i)
    return result

double_everything_in([1, 2, 3, 4, 5])

quadruple_everything_in([1, 2, 3, 4, 5])

### DRY - Fundamental Programming Concept

- The above code violates the ["do not repeat yourself"](https://en.wikipedia.org/wiki/Don't_repeat_yourself_) principle of good software engineering practice.

- How can rewrite the code so that it avoids duplication?

def multiply_by_x_everything_in(x, data):
    result = []
    for i in data:
        result.append(x * i)
    return result

multiply_by_x_everything_in(2, [1, 2, 3, 4, 5])

multiply_by_x_everything_in(4, [1, 2, 3, 4, 5])

- Now consider the following code:

def squared(x):
    return x*x

def double(x):
    return x*2

def square_everything_in(data):
    result = []
    for i in data:
        result.append(squared(i))
    return result

def double_everything_in(data):
    result = []
    for i in data:
        result.append(double(i))
    return result

square_everything_in([1, 2, 3, 4, 5])

double_everything_in([1, 2, 3, 4, 5])

### DRY - Fundamental Programming Concept
- The above code violates the ["do not repeat yourself"](https://en.wikipedia.org/wiki/Don't_repeat_yourself_) principle of good software engineering practice.

- How can rewrite the code so that it avoids duplication?

### Passing Functions as Values
- Functions can be passed to other functions as values.
-


def apply_f_to_everything_in(f, data):
    result = []
    for x in data:
        result.append(f(x))
    return result

apply_f_to_everything_in(squared, [1, 2, 3, 4, 5])

apply_f_to_everything_in(double, [1, 2, 3, 4, 5])

### Lambda expressions

- We can use anonymous functions to save having to define a function each time we want to use map.

apply_f_to_everything_in(lambda x: x*x, [1, 2, 3, 4, 5])

# Python's `map` function

- Python has a built-in function `map` which is much faster than our version.



map(lambda x: x*x, [1, 2, 3, 4, 5])

## Implementing reduce

- The `reduce` function is an example of a [fold](https://en.wikipedia.org/wiki/Fold_%28higher-order_function%29).

- There are different ways we can fold data.

- The following implements a *left* fold.


def foldl(f, data, z):
    if (len(data) == 0):
        print (z)
        return z
    else:
        head = data[0]
        tail = data[1:]
        print ("Folding", head, "with", tail, "using", z)
        partial_result = f(z, data[0])
        print ("Partial result is", partial_result)
        return foldl(f, tail, partial_result)  

def add(x, y):
    return x + y

foldl(add, [3, 3, 3, 3, 3], 0)

foldl(lambda x, y: x + y, [1, 2, 3, 4, 5], 0)

foldl(lambda x, y: x - y, [1, 2, 3, 4, 5], 0)

(((((0 - 1) - 2) - 3) - 4) - 5)

- Subtraction is neither [commutative](https://en.wikipedia.org/wiki/Commutative_property) nor [associative](https://en.wikipedia.org/wiki/Associative_property), so the order in which apply the fold matters:

(1 - (2 - (3 - (4 - (5 - 0)))))

def foldr(f, data, z):
    if (len(data) == 0):
        return z
    else:
        return f(data[0], foldr(f, data[1:], z))                

foldl(lambda x, y: x - y,  [1, 2, 3, 4, 5], 0)

foldr(lambda x, y: x - y, [1, 2, 3, 4, 5], 0)

## Python's `reduce` function.

- Python's built-in `reduce` function is a *left* fold.

from functools import reduce
reduce(lambda x, y: x + y, [1, 2, 3, 4, 5])

reduce(lambda x, y: x - y, [1, 2, 3, 4, 5], 0)

foldl(lambda x, y: x - y, [1, 2, 3, 4, 5], 0)

# Functional programming and parallelism

- Functional programming lends itself to [parallel programming](https://computing.llnl.gov/tutorials/parallel_comp/#Models).

- The `map` function can easily be parallelised through [data-level parallelism](https://en.wikipedia.org/wiki/Data_parallelism),
    - provided that the function we supply as an argument is *free from* [side-effects](https://en.wikipedia.org/wiki/Side_effect_%28computer_science%29)
        - (which is why we avoid working with mutable data).

- We can see this by rewriting it so:


def perform_computation(f, result, data, i):
    print ("Computing the ", i, "th result...")
    # This could be scheduled on a different CPU
    result[i] = f(data[i])

def my_map(f, data):
    result = [None] * len(data)
    for i in range(len(data)):
        perform_computation(f, result, data, i)
    # Wait for other CPUs to finish, and then..
    return result

my_map(lambda x: x * x, [1, 2, 3, 4, 5])

## A multi-threaded `map` function

from threading import Thread

def schedule_computation_threaded(f, result, data, threads, i):    
    # Each function evaluation is scheduled on a different core.
    def my_job(): 
        print ("Processing data:", data[i], "... ")
        result[i] = f(data[i])
        print ("Finished job #", i)    
        print ("Result was", result[i])       
    threads[i] = Thread(target=my_job)
    
def my_map_multithreaded(f, data):
    n = len(data)
    result = [None] * n
    threads = [None] * n
    print ("Scheduling jobs.. ")
    for i in range(n):
        schedule_computation_threaded(f, result, data, threads, i)
    print ("Starting jobs.. ")
    for i in range(n):
        threads[i].start()
    print ("Waiting for jobs to finish.. ")
    for i in range(n):
        threads[i].join()
    print ("All done.")
    return result

my_map_multithreaded(lambda x: x*x, [1, 2, 3, 4, 5])

from numpy.random import uniform
from time import sleep

def a_function_which_takes_a_long_time(x):
    sleep(uniform(2, 10))  # Simulate some long computation
    return x*x

my_map_multithreaded(a_function_which_takes_a_long_time, [1, 2, 3, 4, 5])

## Map Reduce

- Map Reduce is a _programming model_ for scalable parallel processing.
- Scalable here means that it can work on big data with very large compute clusters.
- There are many implementations: e.g. Apache Hadoop and Apache Spark.
- We can use Map-Reduce with any programming language:
    - Hadoop is written in Java
    - Spark is written in Scala, but has a Python interface.
- *Functional programming* languages such as Python or Scala fit very well with the Map Reduce model:
    - However, we don't *have* to use functional programming.

- A MapReduce implementation will take care of the low-level functionality so that you don't have to worry about:
    - load balancing
    - network I/O
    - network and disk transfer optimisation
    - handling of machine failures
    - serialization of data
    - etc..
- The model is designed to move the processing to where the data resides.

## Typical steps in a Map Reduce Computation

1. ETL a big data set.
2. _Map_ operation: extract something you care about from each row
3. "Shuffle and Sort": task/node allocation
4. _Reduce_ operation: aggregate, summarise, filter or transform
5. Write the results.

## Callbacks for Map Reduce

- The data set, and the state of each stage of the computation, is represented as a set of key-value pairs.

- The programmer provides a map function:

$\operatorname{map}(k, v) \rightarrow \; \left< k', v' \right>*$  

- and a reduce function:

$\operatorname{reduce}(k', \left< k', v'\right> *) \rightarrow \; \left< k', v''
\right> *$

- The $*$ refers to a *collection* of values.

- These collections are *not* ordered.

## Word Count Example

- In this simple example, the input is a set of URLs, each record is a document.

- Problem: compute how many times each word has occurred across data set.

## Word Count: Map 


- The input to $\operatorname{map}$ is a mapping:

- Key: URL
- Value: Contents of document

$\left< document1, to \; be \; or \; not \; to \; be \right>$  
    

- In this example, our $\operatorname{map}$ function will process a given URL, and produces a mapping:

- Key: word
- Value: 1

- So our original data-set will be transformed to:
  
  $\left< to, 1 \right>$
  $\left< be, 1 \right>$
  $\left< or, 1 \right>$
  $\left< not, 1 \right>$
  $\left< to, 1 \right>$
  $\left< be, 1 \right>$

## Word Count: Reduce


- The reduce operation groups values according to their key, and then performs areduce on each key.

- The collections are partitioned across different storage units, therefore.

- Map-Reduce will fold the data in such a way that it minimises data-copying across the cluster.

- Data in different partitions are reduced separately in parallel.

- The final result is a reduce of the reduced data in each partition.

- Therefore it is very important that our operator *is both commutative and associative*.

- In our case the function is the `+` operator

  $\left< be, 2 \right>$  
  $\left< not, 1 \right>$  
  $\left< or, 1 \right>$  
  $\left< to, 2 \right>$  
  

## Map and Reduce compared with Python

- Notice that these functions are formulated differently from the standard Python functions of the same name.

- The `reduce` function works with key-value *pairs*.

- It would be more apt to call it something like `reduceByKey`.


## MiniMapReduce

- To illustrate how the Map-Reduce programming model works, we can implement our own Map-Reduce framework in Python.

- This *illustrates* how a problem can be written in terms of `map` and `reduce` operations.

- Note that these are illustrative functions; this is *not* how Hadoop or Apache Spark actually implement them.

##########################################################
#
#   MiniMapReduce
#
# A non-parallel, non-scalable Map-Reduce implementation
##########################################################

def groupByKey(data):
    result = dict()
    for key, value in data:
        if key in result:
            result[key].append(value)
        else:
            result[key] = [value]
    return result
        
def reduceByKey(f, data):
    key_values = groupByKey(data)
    return map(lambda key: 
                   (key, reduce(f, key_values[key])), 
                       key_values)

## Word-count using MiniMapReduce


data = map(lambda x: (x, 1), "to be or not to be".split())
data

groupByKey(data)

reduceByKey(lambda x, y: x + y, data)

## Parallelising MiniMapReduce

- We can easily turn our Map-Reduce implementation into a parallel, multi-threaded framework
by using the `my_map_multithreaded` function we defined earlier.

- This will allow us to perform map-reduce computations that exploit parallel processing using *multiple* cores on a *single* computer.

def reduceByKey_multithreaded(f, data):
    key_values = groupByKey(data)
    return my_map_multithreaded(
        lambda key: (key, reduce(f, key_values[key])), key_values.keys())

reduceByKey_multithreaded(lambda x, y: x + y, data)

## Parallelising the reduce step

- Provided that our operator is both associative and commutative we can
also parallelise the reduce operation.

- We partition the data into approximately equal subsets.

- We then reduce each subset independently on a separate core.

- The results can be combined in a final reduce step.

### Partitioning the data

def split_data(data, split_points):
    partitions = []
    n = 0
    for i in split_points:
        partitions.append(data[n:i])
        n = i
    partitions.append(data[n:])
    return partitions

data = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
partitioned_data = split_data(data, [3])
partitioned_data

### Reducing across partitions in parallel

from threading import Thread

def parallel_reduce(f, partitions):

    n = len(partitions)
    results = [None] * n
    threads = [None] * n
    
    def job(i):
        results[i] = reduce(f, partitions[i])

    for i in range(n):
        threads[i] = Thread(target = lambda: job(i))
        threads[i].start()
    
    for i in range(n):
        threads[i].join()
    
    return reduce(f, results)

parallel_reduce(lambda x, y: x + y, partitioned_data)

## Map-Reduce on a cluster of computers

- The code we have written so far will *not* allow us to exploit parallelism from multiple computers in a [cluster](https://en.wikipedia.org/wiki/Computer_cluster).

- Developing such a framework would be a very large software engineering project.

- There are existing frameworks we can use:
    - [Apache Hadoop](https://hadoop.apache.org/)
    - [Apache Spark](https://spark.apache.org/)
    
- In the next notebook we will cover Apache Spark.