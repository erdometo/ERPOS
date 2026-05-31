using System;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Options;
using Aspire.Hosting;
using Aspire.Hosting.Python;

var builder = DistributedApplication.CreateBuilder(args);

builder.Configuration["ASPNETCORE_URLS"] = "http://localhost:18888";
builder.Configuration["DOTNET_DASHBOARD_OTLP_ENDPOINT_URL"] = "http://localhost:18889";
builder.Configuration["ASPIRE_ALLOW_UNSECURED_TRANSPORT"] = "true";

var dcpOptionsType = typeof(DistributedApplication).Assembly.GetType("Aspire.Hosting.Dcp.DcpOptions");
if (dcpOptionsType != null)
{
    var myConfigureType = typeof(MyConfigureOptions<>).MakeGenericType(dcpOptionsType);
    builder.Services.AddSingleton(typeof(IConfigureOptions<>).MakeGenericType(dcpOptionsType), myConfigureType);
}

// Python Backend API
var backend = builder.AddPythonProject("backend", "../../backend", "main.py", "../venv")
    .WithHttpEndpoint(port: 8000, env: "PORT")
    .WithEnvironment("PYTHONUNBUFFERED", "1")
    .WithEnvironment("NEO4J_URI", "bolt://localhost:7687")
    .WithEnvironment("NEO4J_USER", "neo4j")
    .WithEnvironment("NEO4J_PASSWORD", "password")
    .WithEnvironment("QDRANT_HOST", "localhost")
    .WithEnvironment("QDRANT_PORT", "6333");

// Python Background Worker
var worker = builder.AddPythonProject("worker", "../../backend", "worker.py", "../venv")
    .WithEnvironment("PYTHONUNBUFFERED", "1")
    .WithEnvironment("NEO4J_URI", "bolt://localhost:7687")
    .WithEnvironment("NEO4J_USER", "neo4j")
    .WithEnvironment("NEO4J_PASSWORD", "password")
    .WithEnvironment("QDRANT_HOST", "localhost")
    .WithEnvironment("QDRANT_PORT", "6333");

// React Frontend UI
var frontend = builder.AddNpmApp("frontend", "../../frontend", "dev")
    .WithReference(backend)
    .WithHttpEndpoint(port: 5173, env: "PORT")
    .WithExternalHttpEndpoints();

builder.Build().Run();

public class MyConfigureOptions<T> : IConfigureOptions<T> where T : class
{
    public void Configure(T options)
    {
        var type = options.GetType();
        if (type.FullName == "Aspire.Hosting.Dcp.DcpOptions")
        {
            type.GetProperty("CliPath")?.SetValue(options, @"C:\Users\ASUS\.nuget\packages\aspire.hosting.orchestration.win-x64\8.1.0\tools\dcp.exe");
            type.GetProperty("DashboardPath")?.SetValue(options, @"C:\Users\ASUS\.nuget\packages\aspire.dashboard.sdk.win-x64\8.0.0\tools");
        }
    }
}
