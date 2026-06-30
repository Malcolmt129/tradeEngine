import { useEffect, useState } from "react";

export default function Portfolio() {


  const [portfolio, setPortfolio] = useState<Record<string, unknown>[]>([])
  const [error, setError] = useState<string>("")

  useEffect(() => {
    const fetchPortfolio = async () => {
      try {
        const res = await fetch("/api/account/portfolio")
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        setPortfolio(data.res)
      } catch (err) {
        setError((err as Error).message);
      }
    }

    fetchPortfolio()
  }, [])

  const headers = portfolio.length > 0 ? Object.keys(portfolio[0]) : []

  return (
    <>
      {error && <p>{error}</p>}
      <table>
        <thead>
          <tr>
            {headers.map(key => <th key={key}>{key}</th>)}
          </tr>
        </thead>
        <tbody>
          {portfolio.map((item, i) => (
            <tr key={i}>
              {headers.map(key => <td key={key}>{String(item[key] ?? "")}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </>
  )
}
