using System;
using Microsoft.Extensions.Hosting;

var builder = DistributedApplication.CreateBuilder(args);

// External Container / Cloud Resources
var rabbitmq = builder.AddRabbitMQ("rabbitmq");

var neo4j = builder.AddContainer("neo4j", "neo4j")
    .WithHttpEndpoint(port: 7474, targetPort: 7474, name: "http")
    .WithEndpoint(port: 7687, targetPort: 7687, name: "bolt")
    .WithEnvironment("NEO4J_AUTH", "none");

var qdrant = builder.AddQdrant("qdrant");

// Python Backend API
var backend = builder.AddPythonApp("backend", "../../backend", "main.py")
    .WithHttpEndpoint(port: 8000, env: "PORT")
    .WithReference(rabbitmq)
    .WithReference(neo4j)
    .WithReference(qdrant);

// Python Background Worker
var worker = builder.AddPythonApp("worker", "../../backend", "worker.py")
    .WithReference(rabbitmq)
    .WithReference(neo4j)
    .WithReference(qdrant);

// React Frontend UI
var frontend = builder.AddNpmApp("frontend", "../../frontend", "dev")
    .WithReference(backend)
    .WithHttpEndpoint(port: 5173, env: "PORT")
    .WithExternalHttpEndpoints();

builder.Build().Run();
