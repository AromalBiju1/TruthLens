"use client";
import { useEffect,useState } from "react";
import { useParams } from "next/navigation";
import AnalysisProgress from '../../components/AnalysisProgress';
import VerdictCard from '../../components/VerdictCard';
import ReverseSearchResults from '../../components/ReverseSearchResults';
import AgentLog from '../../components/AgentLog';
import logo from '../../assets/logo.png'
import HeatmapViewer from '../../components/HeatmapViewer'
export type AnalysisStep = {
    id:string,
    label:string,
    status : "pending" | "running" | "done" | "error";
    detail?:string
}


export type AnalysisResult = {
    verdict: "LIKELY REAL" |"LIKELY AI GENERATED" | "INCONCLUSIVE";
    confidence :number
    ml_score : number
    frequency_score : number
    summary :string
    reverse_search : {url :string;title:string;thumbnail:string;date?:string}[];
    agent_reasoning: string[];
    heatmap? :string;

}


const INITIAL_STEPS: AnalysisStep[]= [
{ id: "upload", label: "Processing upload", status: "pending" },
  { id: "face", label: "Extracting faces", status: "pending" },
  { id: "ml", label: "Running CNN ensemble", status: "pending" },
  { id: "frequency", label: "Frequency domain analysis", status: "pending" },
  { id: "exif", label: "Reading EXIF metadata", status: "pending" },
  { id: "reverse", label: "Reverse image search", status: "pending" },
  { id: "agent", label: "AI agent synthesizing verdict", status: "pending" },


];

export default function ResultsPage() {
    const {id} = useParams();
    const [steps,setSteps] = useState<AnalysisStep[]>(INITIAL_STEPS);
    const [ result,setResult] = useState<AnalysisResult | null>(null);
    const [connected,setConnected] = useState(false)



    useEffect(()=>{
        const wsurl = `${process.env.NEXT_PUBLIC_API_URL?.replace("http","ws")}/ws/${id}`
        const ws = new WebSocket(wsurl)


        ws.onopen = () => setConnected(true);
        ws.onmessage = (event) => {
            const msg = JSON.parse(event.data);
            if(msg.type === "step_update"){
                setSteps((prev) =>
                    prev.map((s)=> (s.id === msg.step_id? {...s,status : msg.status,detail:msg.detail}: s))
                )
            }

            if(msg.type === "result"){
                setResult(msg.data)
            }
        }


            ws.onclose = () => setConnected(false)

            return () => ws.close()
        },[id]);


        const iscomplete = result != null

        return (
    <main className="min-h-screen bg-[#0a0a0f] text-white">
      {/* Nav */}
      <nav className="border-b border-white/10 px-6 py-4 flex items-center justify-between">
        <a href="/" className="flex items-center gap-2">
         <div className="flex items-center gap-3 cursor-pointer">
  {/* The Icon */}
  <img 
    src={logo.src} 
    alt="TruthLens Icon" 
    className="h-10 w-10 object-contain mix-blend-screen opacity-90" 
  />
  
  {/* The Text */}
  <span className="font-mono text-xl font-bold tracking-tight text-white">
    Truth<span className="text-[#00ff46]">Lens</span>
  </span>
</div>
        </a>
        <span className={`text-xs px-2 py-1 rounded-full ${connected ? "bg-green-500/20 text-green-400" : "bg-white/10 text-white/40"}`}>
          {connected ? "● Live" : "○ Connecting..."}
        </span>
      </nav>

      <div className="max-w-4xl mx-auto px-6 py-12 space-y-8">
        <div>
          <h1 className="text-2xl font-bold mb-1">Analysis in Progress</h1>
          <p className="text-white text-sm">Job ID: {id}</p>
        </div>

        {/* Progress Steps */}
        <AnalysisProgress steps={steps} />

        {/* Results — shown once complete */}
        {iscomplete && result && (
          <>
            <VerdictCard result={result} />
             <HeatmapViewer heatmap={result.heatmap} />
            <AgentLog reasoning={result.agent_reasoning} />
            {result.reverse_search.length > 0 && (
              <ReverseSearchResults results={result.reverse_search} />
            )}
          </>
        )}
      </div>
    </main>
  );
}









