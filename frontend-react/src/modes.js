import {
  MessageSquare, Terminal, Boxes, HardDrive, Container,
  Wand2, FileSearch, Calculator as CalcIcon,
} from "lucide-react";

export const MODES = [
  {
    id: "chat", group: "Assistants", label: "AI Chat", icon: MessageSquare,
    title: "Ask anything about your infrastructure",
    desc: "Get an explanation, root cause, commands and references from your own docs.",
    placeholder: "e.g. How do I fix CrashLoopBackOff?",
    examples: ["How do I fix CrashLoopBackOff?", "Why is my pod pending?", "What is RAID 10?", "Explain Docker networking"],
  },
  {
    id: "linux", group: "Assistants", label: "Linux", icon: Terminal,
    title: "Linux Troubleshooter",
    desc: "Paste an error or symptom. Get likely causes, checks and a safe fix.",
    placeholder: "e.g. No space left on device",
    examples: ["No space left on device", "How to troubleshoot SSH failure?", "Explain journalctl"],
  },
  {
    id: "kubernetes", group: "Assistants", label: "Kubernetes", icon: Boxes,
    title: "Kubernetes Assistant",
    desc: "Understand pod states: meaning, causes, logs and describe commands, and the fix.",
    placeholder: "e.g. Pod STATUS is CrashLoopBackOff",
    examples: ["Pod STATUS is CrashLoopBackOff", "Pod stuck in Pending", "kubectl logs --previous explained"],
  },
  {
    id: "storage", group: "Assistants", label: "Storage", icon: HardDrive,
    title: "Storage Assistant",
    desc: "LVM, RAID, filesystems, NFS, iSCSI, multipath, SAN and NAS.",
    placeholder: "e.g. How do I extend an LVM logical volume with XFS?",
    examples: ["LVM extension", "NFS vs SMB", "iSCSI login process", "Explain Multipath"],
  },
  {
    id: "docker", group: "Assistants", label: "Docker", icon: Container,
    title: "Docker Assistant",
    desc: "Diagnose crashing containers, exit codes, networking and restart policies.",
    placeholder: "e.g. Container restarting continuously",
    examples: ["Container restarting continuously", "Explain Docker networking"],
  },
  {
    id: "command", group: "Tools", label: "Command Generator", icon: Wand2,
    title: "Command Generator",
    desc: "Describe a task in plain English and get the exact commands.",
    placeholder: "e.g. Create user kishore",
    examples: ["Create user kishore", "Open port 8080 in the firewall", "Find files larger than 1GB"],
  },
  {
    id: "logs", group: "Tools", label: "Log Analyzer", icon: FileSearch,
    title: "Log Analyzer",
    desc: "Paste log lines. Get what happened, the root cause and the fix.",
    placeholder: "Paste logs here, e.g. Failed to start docker.service",
    examples: ["Failed to start docker.service", "kubelet: failed to pull image: ErrImagePull"],
    tall: true,
  },
  {
    id: "calculator", group: "Tools", label: "Storage Calculator", icon: CalcIcon,
    title: "Storage Calculator",
    desc: "Exact RAID sizing in code, not AI guesswork.",
    custom: true,
  },
];
