<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <title>MASGISTICS | Mission Control</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #050505; color: #e5e5e5; font-family: sans-serif; }
        .glass-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); }
        input, select { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.1) !important; color: white !important; }
    </style>
</head>
<body class="p-8">
    <!-- Header -->
    <div class="flex justify-between items-end mb-12 border-b border-white/10 pb-6">
        <div class="flex items-center gap-4">
            <img src="/static/logo.png" alt="Logo" class="h-12 w-auto">
            <div>
                <h1 class="text-4xl font-black tracking-tighter uppercase italic text-white">MASGISTICS</h1>
                <p class="text-[10px] tracking-[0.3em] text-white/50 uppercase font-bold">Orbital Payload Command</p>
            </div>
        </div>
        <div class="text-right">
            <p class="font-mono text-[10px] text-green-500 animate-pulse font-bold uppercase">● System Nominal - Unit 2 Active</p>
        </div>
    </div>

    <!-- Stats Dashboard -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12 text-center">
        <div class="glass-card p-4 border-t-2 border-t-cyan-500">
            <p class="text-[10px] uppercase text-white/40 mb-1 font-bold">Personnel</p>
            <h2 class="text-3xl font-light">{{ users|length }}</h2>
        </div>
        <div class="glass-card p-4 border-t-2 border-t-green-500 text-green-400">
            <p class="text-[10px] uppercase text-white/40 mb-1 font-bold">Open Payloads</p>
            <h2 class="text-3xl font-light">{{ jobs_count }}</h2>
        </div>
        <div class="glass-card p-4 border-t-2 border-t-yellow-500 text-yellow-500">
            <p class="text-[10px] uppercase text-white/40 mb-1 font-bold">Cargo Value</p>
            <h2 class="text-3xl font-light italic">฿{{ "{:,.0f}".format(total_value) }}</h2>
        </div>
        <div class="glass-card p-4 border-t-2 border-t-red-500 bg-red-500/5 shadow-[0_0_15px_rgba(239,68,68,0.2)]">
            <p class="text-[10px] uppercase text-red-400 mb-1 font-bold tracking-widest">Net Revenue</p>
            <h2 class="text-3xl font-bold italic">฿{{ "{:,.0f}".format(potential_revenue) }}</h2>
        </div>
    </div>

    <!-- AI MATCHING INTELLIGENCE (The Heart of Unit 2) -->
    <div class="mb-12 glass-card overflow-hidden border-t-2 border-t-purple-500">
        <div class="p-4 bg-purple-500/10 flex justify-between items-center border-b border-white/10">
            <h3 class="text-sm font-bold uppercase tracking-widest text-purple-400 italic">AI Matching Intelligence</h3>
            <span class="text-[10px] text-white/30 font-mono">Real-time Optimization Active</span>
        </div>
        <div class="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {% for job in jobs %}
            <div class="p-4 border border-white/10 rounded bg-white/5">
                <p class="text-[10px] uppercase text-white/40 mb-2 italic">Waiting for Assignment</p>
                <h4 class="text-md font-bold text-white mb-1">{{ job.title }}</h4>
                <p class="text-xs text-cyan-400 font-mono mb-4">{{ job.origin }} ➔ {{ job.destination }}</p>
                
                <form action="/admin/assign-job" method="post" class="space-y-2">
                    <input type="hidden" name="job_id" value="{{ job.id }}">
                    <select name="user_id" class="w-full p-2 text-[10px] rounded bg-black text-white border border-white/20 font-bold" required>
                        <option value="">เลือกนักบิน (Verified Only)</option>
                        {% for carrier in verified_carriers %}
                        <option value="{{ carrier.id }}">{{ carrier.full_name }} (฿{{ carrier.wallet_balance }})</option>
                        {% endfor %}
                    </select>
                    <button type="submit" class="w-full bg-purple-600 hover:bg-purple-500 text-white text-[10px] py-2 uppercase font-black tracking-widest transition">
                        Match & Execute (฿50)
                    </button>
                </form>
            </div>
            {% endfor %}
            {% if not jobs %}
            <div class="col-span-full p-10 text-center text-white/20 uppercase tracking-[0.5em] italic">No Open Payloads to Match</div>
            {% endif %}
        </div>
    </div>

    <!-- Personnel & Deployment Sections (เหมือนเดิม) -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Deploy Form -->
        <div class="glass-card p-6 h-fit">
            <h3 class="text-sm font-bold uppercase tracking-widest mb-6 border-b border-white/10 pb-2 italic text-cyan-500">Deploy Payload</h3>
            <form action="/admin/add-job" method="post" class="space-y-4">
                <input type="text" name="title" placeholder="Job Title" class="w-full p-2 text-xs rounded" required>
                <div class="grid grid-cols-2 gap-4">
                    <input type="text" name="origin" placeholder="Origin" class="w-full p-2 text-xs rounded" required>
                    <input type="text" name="destination" placeholder="Destination" class="w-full p-2 text-xs rounded" required>
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <select name="truck_type" class="w-full p-2 text-xs rounded text-black font-bold">
                        <option>6 ล้อ</option>
                        <option>10 ล้อ</option>
                        <option>เทรลเลอร์</option>
                    </select>
                    <input type="number" name="price" placeholder="Value (THB)" class="w-full p-2 text-xs rounded font-mono" required>
                </div>
                <button type="submit" class="w-full bg-white text-black py-4 mt-4 text-xs font-bold uppercase tracking-widest hover:bg-gray-200 transition">Execute Launch</button>
            </form>
        </div>

        <!-- Personnel Table -->
        <div class="lg:col-span-2 glass-card overflow-hidden">
            <h3 class="p-4 text-sm font-bold uppercase tracking-widest border-b border-white/10 bg-white/5 text-white italic">Personnel Management</h3>
            <table class="w-full text-left text-sm text-white/80">
                <thead>
                    <tr class="text-[10px] uppercase text-white/40 border-b border-white/10 bg-black/40">
                        <th class="p-4">Identifier</th>
                        <th class="p-4 text-center">Wallet</th>
                        <th class="p-4 text-right">Command</th>
                    </tr>
                </thead>
                <tbody>
                    {% for user in users %}
                    <tr class="border-b border-white/5 hover:bg-white/5 transition-colors">
                        <td class="p-4">
                            <span class="font-bold text-white">{{ user.full_name }}</span>
                            <p class="text-[10px] text-white/30 uppercase italic">{{ user.role }}</p>
                        </td>
                        <td class="p-4 text-center font-mono text-yellow-500 font-bold bg-yellow-500/5">฿{{ "{:,.0f}".format(user.wallet_balance if user.wallet_balance else 0) }}</td>
                        <td class="p-4 text-right">
                            <div class="flex justify-end gap-2">
                                <form action="/admin/topup/{{ user.id }}" method="post" class="flex gap-1">
                                    <input type="number" name="amount" placeholder="฿" class="w-16 p-1 text-[10px] rounded" required>
                                    <button class="bg-cyan-600 text-white text-[10px] px-2 py-1 uppercase font-bold">Topup</button>
                                </form>
                                {% if not user.is_verified %}
                                <form action="/admin/verify/{{ user.id }}" method="post">
                                    <button class="border border-white/30 text-white text-[10px] px-2 py-1 uppercase font-bold hover:bg-white hover:text-black">Verify</button>
                                </form>
                                {% endif %}
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>