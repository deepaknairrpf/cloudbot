# Cloudbot demo with Zipkin and Prometheus integration

This demo shows how to

* integrate [py_zipkin](https://github.com/Yelp/py_zipkin/) in a Python project that uses Flask
    * with separate [client](https://github.com/sebastienvercammen/flask-zipkin-demo/blob/master/services/1/main.py#L41) and [server](https://github.com/sebastienvercammen/flask-zipkin-demo/blob/master/services/1/main.py#L53-L60) Zipkin spans (see [`Client` vs `Server` start/finish](https://github.com/sebastienvercammen/flask-zipkin-demo/blob/master/docs/Client%20Span%20Annotations.png))
    * with [manually added binary annotations](https://github.com/sebastienvercammen/flask-zipkin-demo/blob/master/services/1/main.py#L61) (see `user_headers` [in the bottom right](https://raw.githubusercontent.com/sebastienvercammen/flask-zipkin-demo/master/docs/Trace.png))
    * with an [intentional 50% chance to raise an exception](https://github.com/sebastienvercammen/flask-zipkin-demo/blob/master/services/2/main.py#L43-L45) so it can be traced
* use Docker to build and deploy the services
    * with [`env_file`](https://github.com/sebastienvercammen/flask-zipkin-demo/blob/master/docker-compose.yml#L17-L18) for configuration defaults and [`environment`](https://github.com/sebastienvercammen/flask-zipkin-demo/blob/master/docker-compose.yml#L19-L20) for customization
* [visualize Zipkin traces with the Zipkin UI](https://github.com/sebastienvercammen/flask-zipkin-demo#result)

Table of Contents
=================

* [Distributed tracing demo with Zipkin and Flask](#distributed-tracing-demo-with-zipkin-and-flask)
    * [Demo Request Flow](#demo-request-flow)
    * [Notes](#notes)
        * [General](#general)
        * [Scaling](#scaling)
    * [Running the Demo](#running-the-demo)
        * [Requirements](#requirements)
        * [Usage](#usage)
        * [Removing the Services](#removing-the-services)
    * [Results](#results)
        * [Visualization of the trace via the Zipkin UI](#visualization-of-the-trace-via-the-zipkin-ui)
        * [Client vs Server spans](#client-vs-server-spans)
        * [Exception Traces](#exception-traces)
    * [Resources](#resources)
        * [Articles](#articles)

## Demo Request Flow

![Request Flow](https://github.com/sebastienvercammen/flask-zipkin-demo/blob/master/docs/Request%20Flow.png)

```
User
    -> Service 1
        -> Service 2
            -> Service 3
        -> Service 3
```

## Notes

### General

* Don't use [flask-zipkin](https://github.com/qiajigou/flask-zipkin). It's unmaintained, uses outdated reqs, and has unresolved bugs.
    * Use [py_zipkin](https://github.com/Yelp/py_zipkin/) instead
* The request headers being passed are currently hardcoded based on the order of the services, you could instead define a list of headers to pass when they exist
    * This has pros and cons — consider your context
* In case of doubt, [Jaeger supports the Zipkin trace format](https://www.jaegertracing.io/docs/1.18/getting-started/#migrating-from-zipkin)

### Scaling

* Zipkin scales horizontally by adding more collectors
* Adjust the tracing frequency — in most cases, the majority of requests should not be traced
* Not all storage engines scale equally well

## Running the Demo

### Requirements

* Docker

### Usage

1. `docker-compose up --build`
2. Visit _service 1_: `http://localhost:5001`
3. Visualize in Zipkin: `http://localhost:9411/zipkin`

### Removing the Services

* `docker-compose down`

## Results

### Visualization of the trace via the Zipkin UI

Browse to `http://localhost:9411/zipkin`.

![Trace](https://github.com/sebastienvercammen/flask-zipkin-demo/blob/master/docs/Trace.png)

### Client vs Server spans

Client spans are included in the annotations in the Zipkin UI. Other visualizers don't always auto-combine them.

![Client Span Annotations](https://github.com/sebastienvercammen/flask-zipkin-demo/blob/master/docs/Client%20Span%20Annotations.png)

### Exception Traces

The list of traces with success and exception traces.

![Trace List](https://github.com/sebastienvercammen/flask-zipkin-demo/blob/master/docs/Trace%20List.png)

A specific trace that raised an intentional exception.

![Exception Trace](https://github.com/sebastienvercammen/flask-zipkin-demo/blob/master/docs/Exception%20Trace.png)

## Resources

* [Zipkin](https://zipkin.io/)
* [Yelp/py_zipkin](https://github.com/Yelp/py_zipkin)
* [openzipkin/b3-propagation](https://github.com/openzipkin/b3-propagation)
* [OpenTracing: What is Distributed Tracing?](https://opentracing.io/docs/overview/what-is-tracing/)

### Articles

* [Introducing Distributed Tracing in Your Python Application via Zipkin](https://rollout.io/blog/introducing-distributed-tracing-in-your-python-application-via-zipkin/)
* [OpenTracing in NodeJS, GO, Python: What, Why, How?](https://dzone.com/articles/opentracing-in-nodejs-go-python-what-why-how)
* [A Quick Introduction to Distributed Tracing](https://newrelic.com/resources/ebooks/quick-introduction-distributed-tracing)
* [Microservices: Using Distributed Tracing for Monitoring & Troubleshooting](https://cloudacademy.com/blog/microservices-using-distributed-tracing-monitoring-troubleshooting/)
* [The 5 Pillars of Distributed Tracing](https://www.tfir.io/the-5-pillars-of-distributed-tracing/)
* [A guide to the open source distributed tracing landscape](https://developers.redhat.com/blog/2019/05/01/a-guide-to-the-open-source-distributed-tracing-landscape/)


## Setup
* Create docker network called cloud-bot  
``docker network create cloud-bot``

* Spawn containers needed to run Prometheus (from `prometheus` dir)  
``docker-compose -f prometheus-docker-compose.yml``

* Spawn containers needed to run Zipkin (from `cloudbot` dir)
``docker-compose -f zipkin-docker-compose.yml``  


