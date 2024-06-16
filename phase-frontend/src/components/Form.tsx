import { useForm, SubmitHandler } from "react-hook-form"
import axios from 'axios';

type Inputs = {
    link: string
    notes: string
}

const axiosInstance = axios.create({
    baseURL: 'http://127.0.0.1:5000',
    headers: {
      'Content-Type': 'multipart/form-data',
        // 'Content-Type': 'application/json',
    },
});

export default function Form() {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<Inputs>()
  
  const onSubmit: SubmitHandler<Inputs> = async(data) => {
    console.log("Data", data)
    try {
        let result = await axiosInstance.post('/embed_text', data, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        console.log("Result", result)
    } catch (e) {
        console.log(e)
    }
  }

//   console.log(watch("link"))
  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input defaultValue="" {...register("link", {required: true})} />
      {errors.link && <span>This field is required!</span>}

      <input {...register("notes", { required: false })} />

      <input type="submit" value="Submit"/>
    </form>
  )
}