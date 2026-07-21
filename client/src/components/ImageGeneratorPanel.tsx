import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";
import { apiRequest } from "@/lib/queryClient";
import { ImageIcon, Loader2, Download, AlertCircle, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

const SIZES = ["1024x1024", "512x512", "256x256"] as const;

type Size = typeof SIZES[number];

interface GenerateImageResponse {
  url?: string;
  b64_json?: string;
  mimeType?: string;
  provider?: string;
  engine?: string;
  fallbackReason?: string;
}

export default function ImageGeneratorPanel() {
  const { toast } = useToast();
  const [prompt, setPrompt] = useState("");
  const [size, setSize] = useState<Size>("1024x1024");
  const [imageResult, setImageResult] = useState<GenerateImageResponse | null>(null);

  const generateMutation = useMutation({
    mutationFn: async (): Promise<GenerateImageResponse> => {
      const res = await apiRequest("POST", "/api/generate-image", { prompt, size });
      return res.json() as Promise<GenerateImageResponse>;
    },
    onSuccess: (data) => {
      if (!data.url && !data.b64_json) {
        toast({
          title: "Image generation failed",
          description: "The AI provider returned no image data. Try a different prompt.",
          variant: "destructive",
        });
        return;
      }
      setImageResult(data);
    },
    onError: (err: any) => {
      const description =
        err?.message ||
        "Image generation failed. The provider may be unavailable or rejected the prompt.";
      toast({
        title: "Image generation failed",
        description,
        variant: "destructive",
      });
    },
  });

  const imageSrc = imageResult?.url
    ? imageResult.url
    : imageResult?.b64_json
    ? `data:${imageResult.mimeType ?? "image/png"};base64,${imageResult.b64_json}`
    : null;

  function handleGenerate() {
    if (!prompt.trim()) {
      toast({ title: "Prompt required", description: "Enter a description for the image.", variant: "destructive" });
      return;
    }
    setImageResult(null);
    generateMutation.mutate();
  }

  function handleDownload() {
    if (!imageSrc) return;
    const a = document.createElement("a");
    a.href = imageSrc;
    a.download = "dreamco-image.png";
    a.click();
  }

  return (
    <Card className="buddy-card rounded-2xl border border-border/60" data-testid="image-generator-panel">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-3">
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-violet-500/15 border border-violet-500/30">
            <ImageIcon className="h-4 w-4 text-violet-400" />
          </span>
          <div>
            <CardTitle className="text-base">AI Image Generator</CardTitle>
            <CardDescription className="text-xs">AI provider when configured, local image engine by default</CardDescription>
          </div>
          <Badge className="ml-auto bg-violet-500/15 text-violet-400 border-violet-500/30 text-[10px]">BETA</Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        <Textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Describe the image you want to generate…"
          className="min-h-[88px] rounded-xl border-border/60 bg-background/40 text-sm resize-none"
          disabled={generateMutation.isPending}
          data-testid="image-prompt-input"
          onKeyDown={(e) => {
            if (e.key === "Enter" && e.metaKey) handleGenerate();
          }}
        />

        <div className="flex items-center gap-3">
          <Select value={size} onValueChange={(v) => setSize(v as Size)}>
            <SelectTrigger className="w-36 rounded-xl border-border/60 text-xs" data-testid="image-size-select">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {SIZES.map((s) => (
                <SelectItem key={s} value={s}>{s}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Button
            onClick={handleGenerate}
            disabled={generateMutation.isPending || !prompt.trim()}
            className="flex-1 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 text-white"
            data-testid="generate-image-btn"
          >
            {generateMutation.isPending ? (
              <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Generating…</>
            ) : (
              <><Sparkles className="h-4 w-4 mr-2" />Generate Image</>
            )}
          </Button>
        </div>

        {generateMutation.isPending && (
          <div className="space-y-2" data-testid="image-skeleton">
            <Skeleton className="w-full aspect-square rounded-xl" />
          </div>
        )}

        {generateMutation.isError && !generateMutation.isPending && (
          <div
            className="flex items-start gap-3 p-4 rounded-xl border border-red-500/30 bg-red-500/8"
            data-testid="image-error-banner"
          >
            <AlertCircle className="h-4 w-4 text-red-400 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-400">
              {(generateMutation.error as any)?.message ?? "Image generation failed. Try a different prompt."}
            </p>
          </div>
        )}

        {imageSrc && !generateMutation.isPending && (
          <div className="space-y-3" data-testid="image-result">
            {imageResult?.fallbackReason && (
              <p className="rounded-lg border border-amber-500/30 bg-amber-500/10 px-3 py-2 text-xs text-amber-200">
                {imageResult.fallbackReason}
              </p>
            )}
            <img
              src={imageSrc}
              alt="AI generated image"
              className="w-full rounded-xl border border-border/40 object-cover"
              data-testid="generated-image"
            />
            <Button
              variant="outline"
              size="sm"
              onClick={handleDownload}
              className="w-full rounded-xl"
              data-testid="download-image-btn"
            >
              <Download className="h-3.5 w-3.5 mr-2" />Download Image
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
