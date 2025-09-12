import TransactionInfo from "./TransactionInfo"

export default function List(){
    return (
        <div className="w-full h-150  text-white rounded-xl flex flex-col opacity-50 gap-y-1">
            <TransactionInfo />
            <TransactionInfo />
        </div>
    )
}