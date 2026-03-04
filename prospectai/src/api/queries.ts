import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './client';

export interface Lead {
  id: number;
  company_name: string;
  contact_name: string;
  email: string;
  phone: string;
  icp_score: number;
  heat_score: number;
  status: string;
  city: string;
  tags: string[];
}

export function useLeads() {
  return useQuery({
    queryKey: ['leads'],
    queryFn: async () => {
      const { data } = await apiClient.get('/leads/');
      return data as Lead[];
    },
  });
}

export function useDashboardOverview() {
  return useQuery({
    queryKey: ['analytics', 'overview'],
    queryFn: async () => {
      const { data } = await apiClient.get('/analytics/overview');
      return data;
    },
  });
}

export interface SearchJob {
    id: string;
    status: string;
    total_found: number;
    search_queries: string[];
}

export function useMapsJobs() {
    return useQuery({
        queryKey: ['maps_jobs'],
        queryFn: async () => {
            const { data } = await apiClient.get('/multi-search/history');
            return data as SearchJob[];
        },
    });
}

export function useStartScraping() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async (queries: {query: string, location: string}[]) => {
             const { data } = await apiClient.post('/multi-search/', { searches: queries });
             return data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['maps_jobs'] });
        }
    });
}

// pipelines integration
export interface PipelineItem {
  id: number;
  lead_id: number;
  lead_company_name: string;
  lead_contact_name: string;
  lead_email: string;
  lead_icp_score: number;
  lead_heat_score: number;
  lead_tags: string[];
  stage: string;
}

export function usePipelines() {
    return useQuery({
        queryKey: ['pipelines'],
        queryFn: async () => {
            const { data } = await apiClient.get('/pipelines');
            return data as PipelineItem[];
        }
    });
}

// sequences integration
export interface Sequence {
  id: number;
  name: string;
  schedule: string;
  status: string;
  created_at: string;
}

export function useSequences() {
    return useQuery({
        queryKey: ['sequences'],
        queryFn: async () => {
            const { data } = await apiClient.get('/sequences');
            return data as Sequence[];
        }
    });
}

export function useUpdatePipelineStatus() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async ({ id, stage }: { id: number; stage: string }) => {
            const { data } = await apiClient.put(`/pipelines/${id}`, { stage });
            return data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['pipelines'] });
            queryClient.invalidateQueries({ queryKey: ['leads'] });
        }
    });
}

// messages integration
export interface MessageItem {
  id: number;
  lead_id: number;
  lead_contact_name: string;
  message_type: string;
  subject?: string;
  body: string;
  status: string;
  created_at: string;
}

export function useMessages() {
    return useQuery({
        queryKey: ['messages'],
        queryFn: async () => {
            const { data } = await apiClient.get('/messages');
            return data as MessageItem[];
        }
    });
}

