import { useEffect } from "react";

export default function Seo(props: { title: string; description?: string }) {
  useEffect(() => {
    document.title = props.title;
    const desc = props.description ?? "DreamCo Empire OS — AI-powered autonomous wealth-generation system.";

    let meta = document.querySelector('meta[name="description"]') as HTMLMetaElement | null;
    if (!meta) {
      meta = document.createElement("meta");
      meta.name = "description";
      document.head.appendChild(meta);
    }
    meta.content = desc;
  }, [props.title, props.description]);

  return null;
}
