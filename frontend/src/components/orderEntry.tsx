import { useEffect, useRef, useState } from 'react'

type OrderStatus = {
  orderId: number
  status: string
  filled?: number
  remaining?: number
  avgFillPrice?: number
}

type OrderError = {
  orderId: number
  status: 'Error'
  errorCode: number
  errorMessage: string
}

export default function OrderEntry() {

  /* If you want conditional rendering, I guess you need these things to be
     in there own state. 
  */
  const [orderType, setOrderType] = useState('MKT')
  const [secType, setSecType] = useState('STK')

  const [formData, setFormData] = useState({
    //stuff that you need for the order
    ticker: '',
    exchange: '',
    contractExpiry: '',
    quantity: '',
    price: '',
    action: '',

  })
  const [error, setError] = useState<string>("")
  const [orderStatus, setOrderStatus] = useState<OrderStatus | null>(null)
  const confirmationRef = useRef<HTMLDialogElement>(null)

  useEffect(() => {
    if (orderStatus) {
      confirmationRef.current?.showModal()
    }
  }, [orderStatus])

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((prevState) => ({
      ...prevState,
      [name]: value
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError("")
    setOrderStatus(null)

    try {
      const res = await fetch('/api/order', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          quantity: parseInt(formData.quantity),
          price: parseFloat(formData.price) || 0,
          secType,
          orderType
        })
      })

      const data = await res.json()

      if (!res.ok) {
        const detail: string | OrderError = data.detail
        setError(typeof detail === 'string' ? detail : detail.errorMessage)
        return
      }

      setOrderStatus(data as OrderStatus)
    } catch (err) {
      setError((err as Error).message);
    }
  }
  return (
    <>
      <h1>Order Entry</h1>
      <form id="orderForm" onSubmit={handleSubmit}>

        <label>Security Type:
          <select id="secType" value={secType} onChange={(e) => setSecType(e.target.value)}>
            <option value="STK">Stock or ETF</option>
            <option value="OPT">Option</option>
            <option value="FUT">Future</option>
            <option value="CASH">Forex</option>
            <option value="CMDTY">Commodities</option>
          </select>
        </label>

        <label>
          Order Type:
          <select id="orderType" value={orderType} onChange={(e) => setOrderType(e.target.value)}>
            <option value="MKT">Market</option>
            <option value="LMT">Limit</option>
          </select>
        </label>

        <label>
          Ticker:
          <input
            type='text'
            name='ticker'
            placeholder='e.g. MES'
            value={formData.ticker}
            onChange={handleChange}
          />
        </label>

        <label>
          Exchange:
          <input
            type='text'
            name='exchange'
            placeholder='SMART'
            value={formData.exchange}
            onChange={handleChange}
          />
        </label>


        {secType === 'FUT' && (
          <label>
            Contract Expiry:
            <input
              type='text'
              name='contractExpiry'
              value={formData.contractExpiry}
              onChange={handleChange}
            />
          </label>
        )}

        <label>
          Quantity:
          <input
            type='number'
            name='quantity'
            placeholder='10'
            value={formData.quantity}
            onChange={handleChange}
          />
        </label>


        {orderType === 'LMT' && (
          <label>
            Price:
            <input
              type='number'
              name='price'
              value={formData.price}
              onChange={handleChange}
            />
          </label>
        )}

        <div className="order-actions">
          <button type="button" className={formData.action === 'BUY' ? 'active' : ''} onClick={() => setFormData(prev => ({ ...prev, action: 'BUY' }))}>Buy</button>
          <button type="button" className={formData.action === 'SELL' ? 'active' : ''} onClick={() => setFormData(prev => ({ ...prev, action: 'SELL' }))}>Sell</button>
        </div>

        <button type="submit">Submit</button>

      </form>

      {error && <p className="order-error">{error}</p>}

      <dialog ref={confirmationRef} className="order-confirmation" onClose={() => setOrderStatus(null)}>
        {orderStatus && (
          <>
            <h2>Order {orderStatus.status}</h2>
            <p>Order ID: {orderStatus.orderId}</p>
            {orderStatus.filled !== undefined && (
              <p>Filled: {orderStatus.filled}/{(orderStatus.filled ?? 0) + (orderStatus.remaining ?? 0)}</p>
            )}
            {!!orderStatus.avgFillPrice && <p>Avg Fill Price: {orderStatus.avgFillPrice}</p>}
            <button type="button" onClick={() => confirmationRef.current?.close()}>Close</button>
          </>
        )}
      </dialog>
    </>
  )
}

