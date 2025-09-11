import Navbar from "./components/Navbar"


function App() {
  return (
    <div className="flex flex-row p-2 gap-x-4 m-auto min-h-screen max-h-[fit] ">
      <Navbar></Navbar>
      <div className="flex-1  rounded-xl mr-3 border-[1px] border-zinc-700 min-h-screen max-h-[fit] flex">
      </div>
    </div>
  )
}

export default App
