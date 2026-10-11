import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import type { StudioAudioPort } from '../domain/contracts/studio-audio.port';
import { StudioTransport, notesForWindow, studioTimeline } from '../domain/studioTransport';
import type { Score } from '../domain';

export type StudioPlayerProps = {
  score: Score;
  markers?: { time: number; label: string }[];
  compact?: boolean;
  onBack?: () => void;
  onPositionChange?: (seconds: number) => void;
  initialPosition?: number;
  onPlaybackChange?: (playing: boolean) => void;
};
export function useStudioPlayer(
  { score, initialPosition = 0, onPlaybackChange, onPositionChange }: StudioPlayerProps,
  audio: StudioAudioPort,
  initialSettings: { speed: number; countIn?: number } = { speed: 1 },
) {
  const timeline = useMemo(() => studioTimeline(score), [score]);
  const transport = useMemo(() => {
    const value = new StudioTransport(timeline.duration, initialPosition);
    value.setSpeed(initialSettings.speed, 0);
    return value;
  }, [timeline]);
  const [position, setPosition] = useState(transport.snapshot(0).position);
  const [playing, setPlaying] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loadProgress, setLoadProgress] = useState(0);
  const [countdown, setCountdown] = useState(0);
  const settingsRef = useRef(initialSettings);
  settingsRef.current = initialSettings;
  const [error, setError] = useState(false);
  const [speed, setSpeedState] = useState(transport.speed);
  const cursor = useRef(0);
  const resumeVoices = useRef(true);
  const generation = useRef(0);
  const callbacks = useRef({ onPlaybackChange, onPositionChange });
  callbacks.current = { onPlaybackChange, onPositionChange };

  const restartSchedule = useCallback(() => {
    audio.stop();
    cursor.current = audio.now();
    resumeVoices.current = true;
    setPosition(transport.snapshot(audio.now()).position);
  }, [audio, transport]);
  const seek = useCallback(
    (value: number) => {
      generation.current++;
      setLoading(false);
      setCountdown(0);
      transport.seek(value, audio.now());
      restartSchedule();
      callbacks.current.onPositionChange?.(transport.snapshot(audio.now()).position);
    },
    [audio, transport, restartSchedule],
  );
  const changeSpeed = useCallback(
    (value: number) => {
      transport.setSpeed(value, audio.now());
      setSpeedState(transport.speed);
      restartSchedule();
    },
    [audio, transport, restartSchedule],
  );
  const toggle = useCallback(async () => {
    if (loading) {
      generation.current++;
      setLoading(false);
      setCountdown(0);
      return;
    }
    if (transport.playing) {
      transport.pause(audio.now());
      audio.stop();
      setPlaying(false);
      setPosition(transport.snapshot(audio.now()).position);
      callbacks.current.onPositionChange?.(transport.snapshot(audio.now()).position);
      return;
    }
    const ticket = ++generation.current;
    setLoading(true);
    setError(false);
    try {
      await audio.prepare(
        timeline.notes.map((note) => note.pitch),
        (fraction) => {
          if (generation.current === ticket) setLoadProgress(fraction);
        },
        timeline.notes,
      );
      for (let remaining = settingsRef.current.countIn || 0; remaining > 0; remaining--) {
        if (generation.current !== ticket) return;
        setCountdown(remaining);
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }
      if (generation.current === ticket) setCountdown(0);
      if (generation.current !== ticket) return;
      audio.stop();
      cursor.current = audio.now() + 0.03;
      resumeVoices.current = true;
      transport.play(cursor.current);
      setPlaying(true);
    } catch {
      if (generation.current === ticket) setError(true);
    } finally {
      if (generation.current === ticket) setLoading(false);
    }
  }, [audio, timeline, transport, loading]);

  useEffect(() => {
    let live = true;
    void audio
      .preload?.(timeline.notes, (fraction) => {
        if (live) setLoadProgress(fraction);
      })
      .catch(() => undefined);
    return () => {
      live = false;
    };
  }, [audio, timeline]);
  useEffect(() => {
    setPosition(transport.snapshot(0).position);
    setPlaying(false);
    setError(false);
    setLoading(false);
    setSpeedState(transport.speed);
    return () => {
      generation.current++;
      audio.stop();
      callbacks.current.onPlaybackChange?.(false);
    };
  }, [transport, audio, timeline.duration]);
  useEffect(() => {
    callbacks.current.onPlaybackChange?.(playing);
  }, [playing]);
  useEffect(() => {
    if (!playing) return;
    let lastReport = -1;
    const tick = () => {
      const now = audio.now();
      const state = transport.snapshot(audio.outputTime?.() ?? now);
      setPosition(state.position);
      if (state.ended) {
        transport.pause(now);
        // Scheduled note releases and the room tail finish naturally.
        setPlaying(false);
        callbacks.current.onPositionChange?.(state.position);
        return;
      }
      const until = now + 0.15;
      const from = Math.max(cursor.current, now);
      const skippedByThrottle = now > cursor.current + 0.03;
      for (const window of transport.windows(from, until)) {
        if (resumeVoices.current || skippedByThrottle) window.resume = true;
        resumeVoices.current = false;
        for (const sound of notesForWindow(timeline.notes, window))
          audio.sound(
            sound.note.pitch,
            sound.when,
            sound.duration,
            sound.note.velocity,
            sound.offset,
            sound.note.hand,
          );
      }
      cursor.current = until;
      if (Math.floor(now) !== lastReport) {
        callbacks.current.onPositionChange?.(state.position);
        lastReport = Math.floor(now);
      }
    };
    tick();
    const timer = setInterval(tick, 25);
    return () => clearInterval(timer);
  }, [audio, playing, timeline, transport]);
  return {
    timeline,
    position,
    playing,
    loading,
    loadProgress,
    countdown,
    error,
    clearError: () => setError(false),
    speed,
    toggle,
    seek,
    changeSpeed,
  };
}
