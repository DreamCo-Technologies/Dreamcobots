import { useState } from "react";
import AppShell from "@/components/AppShell";
import Seo from "@/components/Seo";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";
import { useToast } from "@/hooks/use-toast";
import { BrainCircuit, Check, ChevronLeft, ChevronRight, FileText, Image, MessageCircle, Sparkles, Video, Mic, ShieldCheck, Rocket } from "lucide-react";
import { Link } from "wouter";

const STEPS = ["Name it", "Tell it the job", "Give it knowledge", "Teach a skill", "Try it", "Make it yours"];
const SOURCES = [
  { id: "documents", label: "Documents", icon: FileText },
  { id: "books", label: "Books I can use", icon: FileText },
  { id: "photos", label: "Photos", icon: Image },
  { id: "videos", label: "Authorized videos", icon: Video },
  { id: "audio", label: "Voice & audio", icon: Mic },
  { id: "conversations", label: "Conversations", icon: MessageCircle },
];
const SKILLS = ["Explain things simply", "Help me learn", "Help me sell", "Help me research", "Help me organize", "Help me write"];

export default function PersonalAIBuilderPage() {
  const { toast } = useToast();
  const [step, setStep] = useState(0);
  const [name, setName] = useState(() => localStorage.getItem("dreamco.personalAI.name") || "");
  const [job, setJob] = useState(() => localStorage.getItem("dreamco.personalAI.job") || "");
  const [sources, setSources] = useState<string[]>([]);
  const [skill, setSkill] = useState("");
  const [personality, setPersonality] = useState("Friendly and clear");
  const [tested, setTested] = useState(false);

  function persist() {
    localStorage.setItem("dreamco.personalAI.name", name.trim());
    localStorage.setItem("dreamco.personalAI.job", job.trim());
    localStorage.setItem("dreamco.personalAI.skill", skill);
    localStorage.setItem("dreamco.personalAI.sources", JSON.stringify(sources));
    localStorage.setItem("dreamco.personalAI.personality", personality);
  }
  function next() { persist(); if (step < STEPS.length - 1) setStep(step + 1); else toast({ title: "Your Personal AI is ready", description: "Your starter configuration has been saved on this device." }); }
  function testAI() { persist(); setTested(true); toast({ title: "Test complete", description: "Your setup passed the beginner smoke test. The live runtime is the next connection." }); }
  function toggleSource(id: string) { setSources(current => current.includes(id) ? current.filter(item => item !== id) : [...current, id]); }

  return (
    <AppShell>
      <Seo title="Build Your Own AI — DreamCo" description="Create a personalized AI without needing to be a developer." />
      <div className="mx-auto max-w-5xl space-y-6 pb-12">
        <div className="flex items-start justify-between gap-4">
          <div>
            <Badge className="mb-3 rounded-full"><Sparkles className="mr-1 h-3 w-3" /> DreamCo Flagship</Badge>
            <h1 className="text-3xl font-bold md:text-5xl">Build Your Own AI</h1>
            <p className="mt-2 max-w-2xl text-muted-foreground">No coding required. Tell Buddy what you want, give your AI approved knowledge, teach it a skill, and see it improve.</p>
          </div>
          <Link href="/pricing"><Button variant="outline" className="rounded-xl">See plans</Button></Link>
        </div>
        <Card className="rounded-2xl p-5">
          <div className="mb-2 flex items-center justify-between text-sm"><span>Step {step + 1} of {STEPS.length}</span><span className="text-muted-foreground">{STEPS[step]}</span></div>
          <Progress value={((step + 1) / STEPS.length) * 100} />
          <div className="mt-4 hidden gap-2 md:flex">{STEPS.map((label, i) => <div key={label} className={`flex-1 text-xs ${i <= step ? "font-semibold" : "text-muted-foreground"}`}>{i + 1}. {label}</div>)}</div>
        </Card>

        {step === 0 && <Card className="rounded-2xl p-6 md:p-8"><h2 className="text-2xl font-semibold">Give your AI a name</h2><p className="mt-1 text-muted-foreground">You can change it anytime.</p><Input value={name} onChange={e => setName(e.target.value)} placeholder="Example: Jordan's Business Buddy" className="mt-6 rounded-xl text-lg" autoFocus /></Card>}

        {step === 1 && <Card className="rounded-2xl p-6 md:p-8"><h2 className="text-2xl font-semibold">What should your AI help you do?</h2><p className="mt-1 text-muted-foreground">Use normal words. Buddy will turn your goal into the right capabilities.</p><Textarea value={job} onChange={e => setJob(e.target.value)} placeholder="Example: Help me run my small business, answer customers, organize my work, and find new leads." className="mt-6 min-h-40 rounded-xl" autoFocus /><div className="mt-4 grid gap-2 md:grid-cols-3">{["Run my business", "Help me study", "Help me sell"].map(example => <Button key={example} variant="outline" className="justify-start rounded-xl" onClick={() => setJob(example)}>{example}</Button>)}</div></Card>}

        {step === 2 && <Card className="rounded-2xl p-6 md:p-8"><h2 className="text-2xl font-semibold">What should it know?</h2><p className="mt-1 text-muted-foreground">Only add material you have the right to use. You control what your AI learns.</p><div className="mt-6 grid gap-3 sm:grid-cols-2 md:grid-cols-3">{SOURCES.map(({ id, label, icon: Icon }) => { const active = sources.includes(id); return <button key={id} onClick={() => toggleSource(id)} className={`rounded-2xl border p-5 text-left transition ${active ? "border-primary bg-primary/10" : "hover:bg-muted/50"}`}><Icon className="mb-3 h-6 w-6" /><div className="font-medium">{label}</div><div className="mt-1 text-xs text-muted-foreground">{active ? "Selected" : "Add later"}</div>{active && <Check className="mt-3 h-4 w-4 text-primary" />}</button>; })}</div><div className="mt-5 flex items-center gap-2 rounded-xl border p-3 text-sm"><ShieldCheck className="h-4 w-4 text-primary" /> Your permission controls decide what can become lasting memory.</div></Card>}

        {step === 3 && <Card className="rounded-2xl p-6 md:p-8"><h2 className="text-2xl font-semibold">Teach it one useful skill</h2><p className="mt-1 text-muted-foreground">Pick a starter skill now. You can build custom skills later.</p><div className="mt-6 grid gap-3 sm:grid-cols-2">{SKILLS.map(item => <button key={item} onClick={() => setSkill(item)} className={`rounded-xl border p-4 text-left ${skill === item ? "border-primary bg-primary/10" : "hover:bg-muted/50"}`}>{skill === item && <Check className="mb-2 h-4 w-4 text-primary" />}{item}</button>)}</div></Card>}

        {step === 4 && <Card className="rounded-2xl p-6 md:p-8"><h2 className="text-2xl font-semibold">Let's see if it is ready</h2><p className="mt-1 text-muted-foreground">This is a setup smoke test, not a claim that your AI is perfect.</p><div className="my-6 rounded-2xl bg-muted/40 p-5"><div className="font-medium">Your starter recipe</div><div className="mt-3 grid gap-2 text-sm"><div><b>Name:</b> {name || "Not set"}</div><div><b>Job:</b> {job || "Not set"}</div><div><b>Knowledge:</b> {sources.join(", ") || "Not set"}</div><div><b>Skill:</b> {skill || "Not set"}</div></div></div><Button onClick={testAI} disabled={!name || !job || !sources.length || !skill} className="rounded-xl"><BrainCircuit className="mr-2 h-4 w-4" />Run my first test</Button>{tested && <div className="mt-4 flex items-center gap-2 text-sm text-primary"><Check className="h-4 w-4" /> Beginner smoke test passed. Live runtime connection is the next step.</div>}</Card>}

        {step === 5 && <Card className="rounded-2xl p-6 md:p-8"><h2 className="text-2xl font-semibold">Make it feel like yours</h2><p className="mt-1 text-muted-foreground">These settings can be changed later.</p><div className="mt-6"><label className="text-sm font-medium">Personality</label><select value={personality} onChange={e => setPersonality(e.target.value)} className="mt-2 w-full rounded-xl border bg-background p-3"><option>Friendly and clear</option><option>Short and direct</option><option>Patient teacher</option><option>Professional business partner</option><option>Creative and energetic</option></select></div><div className="mt-6 rounded-2xl border p-5"><div className="flex items-center gap-2 font-medium"><Rocket className="h-4 w-4" /> Your AI starter profile</div><p className="mt-2 text-sm text-muted-foreground">{name || "Your AI"} is set up to {job || "help you"}, using {sources.length} approved source type(s), with the skill “{skill || "your first skill"}”.</p></div><div className="mt-5 rounded-xl bg-primary/10 p-4 text-sm">Next: connect the live Personal AI runtime, memory vault, model routing, and paid capabilities.</div></Card>}

        <div className="flex justify-between gap-3"><Button variant="outline" disabled={step === 0} onClick={() => setStep(s => s - 1)} className="rounded-xl"><ChevronLeft className="mr-1 h-4 w-4" />Back</Button><Button disabled={(step === 0 && !name.trim()) || (step === 1 && !job.trim()) || (step === 2 && !sources.length) || (step === 3 && !skill) || (step === 4 && !tested)} onClick={next} className="rounded-xl">{step === STEPS.length - 1 ? "Save my AI" : "Continue"}<ChevronRight className="ml-1 h-4 w-4" /></Button></div>
      </div>
    </AppShell>
  );
}
