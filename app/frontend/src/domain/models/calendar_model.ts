export interface Calendar_Comment {
  id: string;
  author_external_id: string;
  author_display_name: string;
  text: string;
  created_at: Date;
}

export interface Calendar_Model {
  id: string;
  title: string;
  color: string;
  owner_id: string; // Mapea a creator_external_id del backend
  creator_display_name?: string;
  keywords?: string[];
  description?: string;
  icon?: string;
  is_public: boolean; // Mapea a visibility === 'public'
  visibility?: "public" | "private" | "unlisted";
  parent_id?: string;
  created_at?: Date;
  updated_at?: Date;
  subscriber_count?: number;
  comments?: Calendar_Comment[];
}
