import { useEffect, useState } from 'react'


export default function OrderEntry() {

  const [formData, setFormData] = useState({
    //stuff that you need for the order
    ticker: '',
    exchange: '',
    secType: '',
    price: '',
    action: ''

  })
  const [orderType, setOrderType] = useState('MKT')
  const [error, setError] = useState<string>("")

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((prevState) => ({
      ...prevState,
      [name]: value
    }));
  };

  const handleSubmit = (event) => {
    event.preventDefault()
    //I think this is where you use fetch to send the data
  }
  return (
    <>
      <h1>Order Entry</h1>
      <form id="orderForm" onSubmit={handleSubmit}>

        <label>Order Type:
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
            placeholder='e.g. MES, MNQ'
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

        <label>
          Security Type:
          <input
            type='text'
            name='secType'
            placeholder='FUT'
            value={formData.secType}
            onChange={handleChange}
          />
        </label>


        <label>
          <button 
        </label>
        {orderType === 'LMT' && (
          <label>
            Price:
            <select id="action" onChange={handleChange}>
              <option value="BUY">Buy</option>
              <option value="SELL">Sell</option>
            </select>
          </label>
        )}

      </form>
    </>
  )
}

