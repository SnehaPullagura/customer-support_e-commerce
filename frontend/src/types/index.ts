export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  permissions: string[];
  customer_id?: string;
  agent_id?: string;
}

export interface Customer {
  id: string;
  external_customer_id?: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  preferred_language: string;
  status: string;
  segment: string;
  tier: string;
  total_orders_count: number;
  lifetime_value_cents: number;
  created_at: string;
}

export interface Case {
  id: string;
  case_number: string;
  customer_id: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  category: string;
  subcategory?: string;
  source: string;
  assigned_agent_id?: string;
  assigned_team_id?: string;
  order_id?: string;
  product_id?: string;
  payment_id?: string;
  shipment_id?: string;
  return_id?: string;
  refund_id?: string;
  sentiment_score?: number;
  frustration_score?: number;
  ai_summary?: string;
  is_escalated: boolean;
  first_response_due_at?: string;
  resolution_due_at?: string;
  first_responded_at?: string;
  resolved_at?: string;
  closed_at?: string;
  created_at: string;
  updated_at: string;
  customer?: Customer;
}

export interface Message {
  id: string;
  conversation_id: string;
  sender_type: 'CUSTOMER' | 'AGENT' | 'BOT' | 'SYSTEM';
  sender_id?: string;
  sender_name: string;
  content: string;
  message_type: string;
  is_internal: boolean;
  sentiment_score?: number;
  created_at: string;
}

export interface Conversation {
  id: string;
  case_id: string;
  channel: string;
  status: string;
  unread_customer_count: number;
  unread_agent_count: number;
  messages: Message[];
  created_at: string;
}

export interface Agent {
  id: string;
  user_id: string;
  team_id?: string;
  employee_code: string;
  display_name: string;
  status: 'AVAILABLE' | 'BUSY' | 'AWAY' | 'OFFLINE' | 'ON_BREAK';
  max_active_cases: number;
  current_active_cases: number;
  tier: string;
  languages: string[];
  csat_score: number;
  avg_resolution_mins: number;
  total_resolved_cases: number;
}

export interface CommerceOrderItem {
  product_id: string;
  sku: string;
  title: string;
  quantity: number;
  unit_price_cents: number;
  total_price_cents: number;
  image_url?: string;
  is_returnable: boolean;
}

export interface CommerceShipmentEvent {
  status: string;
  description: string;
  location?: string;
  timestamp: string;
}

export interface CommerceShipment {
  shipment_id: string;
  order_id: string;
  carrier: string;
  tracking_number: string;
  status: string;
  estimated_delivery?: string;
  delivered_at?: string;
  tracking_history: CommerceShipmentEvent[];
}

export interface CommerceOrder {
  order_id: string;
  order_number: string;
  customer_id: string;
  status: string;
  total_amount_cents: number;
  currency: string;
  placed_at: string;
  delivered_at?: string;
  items: CommerceOrderItem[];
  shipments: CommerceShipment[];
}

export interface CommerceGraph {
  customer?: any;
  active_order?: CommerceOrder;
  recent_orders: CommerceOrder[];
  recent_shipments: CommerceShipment[];
}

export interface PlaybookStep {
  id: string;
  step_order: number;
  step_key: string;
  title: string;
  instructions: string;
  action_type: string;
  is_mandatory: boolean;
}

export interface Playbook {
  id: string;
  code: string;
  name: string;
  category: string;
  description?: string;
  steps: PlaybookStep[];
}

export interface PlaybookExecution {
  id: string;
  case_id: string;
  playbook_id: string;
  status: string;
  current_step_order: number;
  completed_at?: string;
  playbook?: Playbook;
}

export interface KnowledgeArticle {
  id: string;
  slug: string;
  title: string;
  content: string;
  excerpt?: string;
  visibility: string;
  tags: string[];
  view_count: number;
  helpful_votes: number;
}

export interface OperationalMetrics {
  total_cases_created: number;
  total_cases_resolved: number;
  total_tickets_closed: number;
  avg_first_response_time_mins: number;
  avg_resolution_time_hours: number;
  sla_compliance_rate_percent: number;
  escalation_rate_percent: number;
  csat_average: number;
  deflection_rate_percent: number;
}
