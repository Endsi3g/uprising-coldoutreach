import React, { useState, useEffect } from 'react';
import { MoreHorizontal, Plus, GripVertical, Flame, Loader2 } from 'lucide-react';
import { DragDropContext, Droppable, Draggable, DropResult } from '@hello-pangea/dnd';
import { usePipelines, useUpdatePipelineStatus, PipelineItem } from '../api/queries';

const initialColumns = [
  { id: 'New', title: 'Nouveau', color: 'border-secondary/20 bg-secondary/5 text-secondary' },
  { id: 'Contacted', title: 'Contacté', color: 'border-warning/20 bg-warning/5 text-warning' },
  { id: 'Replied', title: 'Répondu', color: 'border-primary/20 bg-primary/5 text-primary' },
  { id: 'Hot', title: 'Chaud', color: 'border-danger/20 bg-danger/5 text-danger' },
  { id: 'Booked', title: 'Rendez-vous', color: 'border-success/20 bg-success/5 text-success' },
];

export function Pipelines() {
  const { data: backendPipelines = [], isLoading } = usePipelines();
  const { mutate: updateStatus } = useUpdatePipelineStatus();
  
  const [cards, setCards] = useState<PipelineItem[]>([]);

  useEffect(() => {
    if (backendPipelines.length > 0) {
      setCards(backendPipelines);
    }
  }, [backendPipelines]);

  const onDragEnd = (result: DropResult) => {
    const { destination, source, draggableId } = result;

    if (!destination) return;

    if (
      destination.droppableId === source.droppableId &&
      destination.index === source.index
    ) {
      return;
    }

    const draggedCard = cards.find(c => c.id.toString() === draggableId);
    if (!draggedCard) return;

    const newCards: PipelineItem[] = [...cards];
    
    // Remove from old position
    const sourceCards = newCards.filter(c => c.stage === source.droppableId);
    sourceCards.splice(source.index, 1);
    
    // Add to new position
    const destCards = newCards.filter(c => c.stage === destination.droppableId && c.id.toString() !== draggableId);
    destCards.splice(destination.index, 0, { ...draggedCard, stage: destination.droppableId });

    // Reconstruct full array
    const otherCards = newCards.filter(c => c.stage !== source.droppableId && c.stage !== destination.droppableId);
    
    if (source.droppableId === destination.droppableId) {
      setCards([...otherCards, ...destCards]);
    } else {
      setCards([...otherCards, ...sourceCards, ...destCards]);
      // Actually trigger DB mutation since stage changed
      updateStatus({ id: draggedCard.id, stage: destination.droppableId });
    }
  };

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary tracking-tight">Pipelines</h1>
          <p className="text-sm text-text-secondary">Suivez l'évolution de vos prospects.</p>
        </div>
        <button className="inline-flex items-center justify-center rounded-xl bg-primary px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-primary-dark transition-colors">
          <Plus className="mr-2 h-4 w-4" />
          Ajouter un Pipeline
        </button>
      </div>

      <div className="flex-1 overflow-x-auto pb-4">
        <DragDropContext onDragEnd={onDragEnd}>
          <div className="flex h-full items-start gap-6">
            {initialColumns.map(column => {
              const columnCards = cards.filter(c => c.stage === column.id);
              return (
                <div 
                  key={column.id} 
                  className="flex h-full w-80 flex-col rounded-xl bg-surface border border-border shrink-0"
                >
                  <div className={`flex items-center justify-between border-b border-border px-4 py-3 rounded-t-xl ${column.color}`}>
                    <h3 className="font-semibold text-sm uppercase tracking-wider">{column.title}</h3>
                    <span className="flex h-6 w-6 items-center justify-center rounded-full bg-background/50 text-xs font-medium">
                      {columnCards.length}
                    </span>
                  </div>
                  
                  <Droppable droppableId={column.id}>
                    {(provided, snapshot) => (
                      <div 
                        ref={provided.innerRef}
                        {...provided.droppableProps}
                        className={`flex-1 overflow-y-auto p-3 space-y-3 transition-colors ${snapshot.isDraggingOver ? 'bg-primary/5' : 'bg-background/30'}`}
                      >
                        {columnCards.map((card, index) => (
                          <Draggable 
                            {...{ key: card.id.toString() } as any}
                            draggableId={card.id.toString()} 
                            index={index}
                          >
                            {(provided, snapshot) => (
                              <div 
                                ref={provided.innerRef}
                                {...provided.draggableProps}
                                {...provided.dragHandleProps}
                                className={`group relative rounded-xl border bg-surface p-4 shadow-sm transition-all ${
                                  snapshot.isDragging ? 'border-primary shadow-lg ring-1 ring-primary' : 'border-border hover:border-primary/50 hover:shadow-md'
                                }`}
                              >
                                <div className="flex items-start justify-between">
                                  <div className="flex items-center gap-3">
                                    <div className="h-8 w-8 shrink-0 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold text-sm uppercase">
                                      {card.lead_company_name ? card.lead_company_name.charAt(0) : '?'}
                                    </div>
                                    <div>
                                      <h4 className="font-semibold text-text-primary text-sm">{card.lead_company_name}</h4>
                                      <p className="text-xs text-text-secondary">{card.lead_contact_name || 'N/A'}</p>
                                    </div>
                                  </div>
                                  <button title="More actions" className="text-text-secondary hover:text-primary opacity-0 group-hover:opacity-100 transition-opacity">
                                    <MoreHorizontal className="h-4 w-4" />
                                  </button>
                                </div>
                                
                                <div className="mt-3 flex items-center gap-4 text-xs">
                                  <div className="flex items-center gap-1">
                                    <span className="text-text-secondary">ICP:</span>
                                    <span className="font-medium text-text-primary">{card.lead_icp_score || '0'}</span>
                                  </div>
                                  <div className="flex items-center gap-1">
                                    <span className="text-text-secondary">Chaleur:</span>
                                    <span className="font-medium text-danger flex items-center gap-0.5"><Flame className="w-3 h-3" /> {card.lead_heat_score || '0'}</span>
                                  </div>
                                </div>

                                <div className="mt-3 flex flex-wrap gap-1">
                                  {(card.lead_tags || []).map((tag, i) => (
                                    <span key={i} className="inline-flex items-center rounded-md bg-background px-2 py-0.5 text-[10px] font-medium text-text-secondary ring-1 ring-inset ring-border">
                                      {tag}
                                    </span>
                                  ))}
                                </div>
                                
                                <div className="absolute left-1 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 text-text-secondary cursor-grab active:cursor-grabbing">
                                  <GripVertical className="h-4 w-4" />
                                </div>
                              </div>
                            )}
                          </Draggable>
                        ))}
                        {provided.placeholder}
                        
                        <button className="flex w-full items-center justify-center gap-2 rounded-xl border border-dashed border-border py-3 text-sm font-medium text-text-secondary hover:border-primary hover:text-primary transition-colors bg-surface/50 mt-3">
                          <Plus className="h-4 w-4" />
                          Ajouter un prospect
                        </button>
                      </div>
                    )}
                  </Droppable>
                </div>
              );
            })}
          </div>
        </DragDropContext>
      </div>
    </div>
  );
}
