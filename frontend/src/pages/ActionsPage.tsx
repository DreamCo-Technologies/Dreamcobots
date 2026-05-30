import React, { useState, useEffect } from "react";

const ActionsPage = () => {
    const [botHealth, setBotHealth] = useState({});
    const [queueHealth, setQueueHealth] = useState({});
    const [logStream, setLogStream] = useState([]);

    useEffect(() => {
        // Fetch monitoring data from FleetMonitor API
        fetch("/api/monitoring/bots")
            .then((res) => res.json())
            .then((data) => setBotHealth(data));

        fetch("/api/monitoring/queue")
            .then((res) => res.json())
            .then((data) => setQueueHealth(data));

        // Example log streaming (replace with WebSocket/EventSource)
        const logExample = [
            "[2026-05-30 12:00:00] Bot Build Started",
            "[2026-05-30 12:00:10] Bot Build Completed",
        ];
        setLogStream(logExample);
    }, []);

    return (
        <div>
            <h1>System Command Center</h1>

            <div>
                <h2>Bot Health</h2>
                <p>Total Bots: {botHealth.total_bots}</p>
                <p>Healthy: {botHealth.healthy}</p>
                <p>Failed: {botHealth.failed}</p>
            </div>

            <div>
                <h2>Queue Health</h2>
                <p>Queue Depth: {queueHealth.queue_depth}</p>
                <p>Stalled Jobs: {queueHealth.stalled_jobs}</p>
            </div>

            <div>
                <h2>Live Logs</h2>
                <ul>
                    {logStream.map((log, index) => (
                        <li key={index}>{log}</li>
                    ))}
                </ul>
            </div>
        </div>
    );
};

export default ActionsPage;