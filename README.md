# Cloudbot with Zipkin and Prometheus Integration

This project is a prototype of a conversational chatbot that understands natural-language queries about cloud workloads and provides rich analytical insights.  
The bot currently supports integrations with Prometheus (popular open-source infrastructure monitoring tool) and Zipkin (a popular open-source distributed tracing tool)  

## Instructions to setup  
* Create the docker network which will be used by all the services  
  `docker network create cloud-bot`  
 
* Spawn Prometheus and related exporters using docker-compose
  `docker-compose -f prometheus/prometheus-docker-compose.yml up`  
  
  * Access prometheus and grafana dashboard at `http://localhost:9090/` and `http://localhost:3000/` respectively  
  * ![Grafana Container Monitoring Dashboard](https://github.com/deepaknairrpf/cloudbot/blob/master/prometheus/screens/Grafana_Docker_Containers.png)
* Spawn Zipkin and the three example microservices using docker-compose  
  `docker-compose -f zipkin-docker-compose.yml up`  
  
  * Access Zipkin dashboard at `http://localhost:9411/`  
  * ![Zipkin Trace](https://github.com/deepaknairrpf/cloudbot/blob/master/docs/Trace.png)
 
* Build the docker image pertaining to the chatbot
  `docker build -t cloudbot .`

* Spawn services used by bot, viz. rasa servers and mongodb using docker-compose
  `docker-compose up`
  * ![Chatbot Dialog Flow](https://github.com/deepaknairrpf/cloudbot/blob/master/docs/chatbot3.png)
  
  
## Demo Request Flow for the simulated microservices APIs

![Request Flow](https://github.com/deepaknairrpf/cloudbot/blob/master/docs/Microservices%20API.png)

```
User
    -> Service 1
        -> Service 2
            -> Service 3
        -> Service 3
```

