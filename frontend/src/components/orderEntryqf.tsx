import { useForm, type SubmitHandler } from 'react-hook-form'


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

type Inputs = {
  ticker: string
  exchange: string
  contractExpiry: string
  quantity: number
  price: number
  action: string

}

export default function OrderEntry2() {


  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<Inputs>()

  const onSubmit: SubmitHandler<Inputs> = (data) => console.log(data)

  return (
    <>
        /* "handleSubmit" will validate your inputs before invoking "onSubmit" */
      <form onSubmit={handleSubmit(onSubmit)}>
        {/* register your input into the hook by invoking the "register" function */}
        <input defaultValue="test" {...register("ticker")} />

        {/* include validation with required or other standard HTML validation rules */}
        <input {...register("exchange", { required: true })} />
        {/* errors will return when field validation fails  */}
        {errors.exchange && <span>This field is required</span>}

        <input type="submit" />
      </form>
    </>
  )
}


