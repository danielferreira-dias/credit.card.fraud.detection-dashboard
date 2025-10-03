export default function DashboardPage(){
    return (
        <div className="flex h-full w-full text-white justify-center items-center bg-zinc-950 min-h-screen max-h-[fit] " style={{
                border: 'double 1px transparent',
                borderRadius: '0.75rem',
                backgroundImage: `
                    linear-gradient(#0a0a0a, #0a0a0a),
                    linear-gradient(135deg, rgba(75, 75, 75, 1) 0%, rgba(10, 10, 10, 1) 25%, rgba(10, 10, 10, 1) 85%, rgba(75, 75, 75, 1) 100%),
                    linear-gradient(225deg, rgba(75, 75, 75, 1) 0%, rgba(10, 10, 10, 1) 15%, rgba(10, 10, 10, 1) 85%, rgba(75, 75, 75, 1) 100%)
                `,
                backgroundOrigin: 'border-box',
                backgroundClip: 'padding-box, border-box, border-box'
            }}>Transactions Page</div>
    )
}

