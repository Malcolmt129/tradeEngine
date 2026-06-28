import { useEffect, useState } from 'react'


function Connection() {

  const [connection, setConnection] = useState<boolean | null>(null)
  const [error, setError] = useState<string>("")
  const [accountValue, setAccountValue] = useState<number>(0.0)

  useEffect(() => {
    const fetchStatus = async () => {
      try {

        const res = await fetch("/api/status");
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        setConnection(data.res)
      } catch (err) {

        setError((err as Error).message);

      }

    }

    const fetchAccountValue = async () => {
      try {

        const res = await fetch("/api/account/value");

        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        setAccountValue(data.res)

      } catch (err) {

        setError((err as Error).message);
      }

    }

    fetchStatus()
    fetchAccountValue()
  }, [])

  const statusLabel = () => {
    if (error) return `Error: ${error}`;
    if (connection === null) return "Checking...";
    return connection ? "Connected" : "Disconnected";
  };
  return (
    <>
      <h1>Dashboard</h1>
      <p> TWS: {statusLabel()}</p>
      <p> AccountValue: {accountValue}</p>

    </>
  )
}

export default Connection
