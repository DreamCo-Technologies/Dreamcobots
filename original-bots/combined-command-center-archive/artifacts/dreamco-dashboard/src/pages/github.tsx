import {
  useListRepos, getListReposQueryKey,
  useListCommits, getListCommitsQueryKey,
  useGetRepoActivity, getGetRepoActivityQueryKey,
} from "@workspace/api-client-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { GitCommit, GitBranch, Star, AlertCircle, ExternalLink, Lock, Globe, Database } from "lucide-react";

export default function Github() {
  const { data: repos, isLoading: loadingRepos } = useListRepos({
    query: { queryKey: getListReposQueryKey() },
  });
  const { data: commits, isLoading: loadingCommits } = useListCommits({
    query: { queryKey: getListCommitsQueryKey() },
  });
  const { data: activity, isLoading: loadingActivity } = useGetRepoActivity({
    query: { queryKey: getGetRepoActivityQueryKey() },
  });

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-mono font-bold tracking-tight text-foreground uppercase flex items-center gap-3">
          <GitBranch className="h-8 w-8 text-primary" />
          Repo_Intelligence
        </h1>
        <p className="text-muted-foreground font-mono text-sm uppercase tracking-wider">
          Source Code Metrics // DreamCo-Technologies
        </p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Repos" value={activity?.totalRepos} loading={loadingActivity} icon={<Database className="h-5 w-5 text-primary" />} />
        <StatCard title="Total Bots" value={activity?.totalBots} loading={loadingActivity} icon={<GitBranch className="h-5 w-5 text-primary" />} />
        <StatCard title="Recent Commits" value={activity?.totalCommits} loading={loadingActivity} icon={<GitCommit className="h-5 w-5 text-primary" />} />
        <StatCard title="Active Repos" value={activity?.activeRepos} loading={loadingActivity} icon={<Star className="h-5 w-5 text-primary" />} />
      </div>

      <Card className="border-border/40 bg-card/50 backdrop-blur">
        <CardHeader>
          <CardTitle className="font-mono text-lg uppercase flex items-center gap-2">
            <Database className="h-5 w-5 text-primary" />
            Repositories
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loadingRepos ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-32 w-full" />)}
            </div>
          ) : (repos || []).length === 0 ? (
            <p className="text-muted-foreground font-mono text-sm text-center py-8">No repositories found</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {repos!.map((repo) => (
                <a
                  key={repo.fullName}
                  href={repo.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group rounded-md border border-border/40 bg-background/50 p-5 hover:border-primary/40 transition-colors block"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        {repo.isPrivate ? <Lock className="h-3.5 w-3.5 text-amber-400 shrink-0" /> : <Globe className="h-3.5 w-3.5 text-primary shrink-0" />}
                        <h3 className="font-mono font-bold text-foreground truncate group-hover:text-primary transition-colors">{repo.name}</h3>
                      </div>
                      {repo.description && (
                        <p className="text-xs text-muted-foreground mt-2 line-clamp-2">{repo.description}</p>
                      )}
                    </div>
                    <ExternalLink className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors shrink-0" />
                  </div>
                  <div className="flex items-center gap-4 mt-4 font-mono text-xs text-muted-foreground">
                    {repo.language && (
                      <span className="text-primary/80">{repo.language}</span>
                    )}
                    <span className="flex items-center gap-1">
                      <Star className="h-3 w-3" /> {repo.stars}
                    </span>
                    <span className="flex items-center gap-1">
                      <GitBranch className="h-3 w-3" /> {repo.forks}
                    </span>
                    {(repo.openIssues ?? 0) > 0 && (
                      <span className="flex items-center gap-1 text-amber-400">
                        <AlertCircle className="h-3 w-3" /> {repo.openIssues}
                      </span>
                    )}
                    <span className="ml-auto">{new Date(repo.updatedAt).toLocaleDateString()}</span>
                  </div>
                </a>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card className="border-border/40 bg-card/50 backdrop-blur">
        <CardHeader>
          <CardTitle className="font-mono text-lg uppercase flex items-center gap-2">
            <GitCommit className="h-5 w-5 text-primary" />
            Commit_Stream
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loadingCommits ? (
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map(i => <Skeleton key={i} className="h-16 w-full" />)}
            </div>
          ) : (commits || []).length === 0 ? (
            <p className="text-muted-foreground font-mono text-sm text-center py-8">No commits yet</p>
          ) : (
            <div className="space-y-2">
              {commits!.map((c, idx) => (
                <a
                  key={`${c.sha}-${idx}`}
                  href={c.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-start gap-4 p-3 rounded-md border border-border/40 bg-background/50 hover:border-primary/40 transition-colors"
                >
                  <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                    <GitCommit className="h-4 w-4 text-primary" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-foreground truncate">{c.message}</p>
                    <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground font-mono flex-wrap">
                      <Badge variant="outline" className="font-mono text-xs border-primary/30 text-primary/80">{c.repoName}</Badge>
                      <span>{c.author}</span>
                      <span>•</span>
                      <span>{new Date(c.date).toLocaleString()}</span>
                    </div>
                  </div>
                  <div className="text-xs font-mono text-muted-foreground shrink-0">{c.sha}</div>
                </a>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function StatCard({ title, value, loading, icon }: { title: string; value?: number; loading: boolean; icon: React.ReactNode }) {
  return (
    <Card className="border-border/40 bg-card/50 backdrop-blur">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <p className="text-xs font-mono text-muted-foreground uppercase tracking-wider">{title}</p>
            {loading ? <Skeleton className="h-8 w-16" /> : (
              <h3 className="text-3xl font-mono font-bold text-foreground">{(value ?? 0).toLocaleString()}</h3>
            )}
          </div>
          <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">{icon}</div>
        </div>
      </CardContent>
    </Card>
  );
}
