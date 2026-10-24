export type ChallengeNote = { pitch: number; onset: number; duration: number; velocity: number };
export type TheoryChallenge = {
  id: string;
  mode: 'keyboard' | 'choice';
  prompt: string;
  explanation: string;
  answerPitches?: number[];
  choices?: { id: string; label: string }[];
  answerChoice?: string;
  audio: ChallengeNote[];
};
export function checkChallenge(
  challenge: TheoryChallenge,
  pitches: number[],
  choice: string | null,
) {
  if (challenge.mode === 'choice') return !!choice && choice === challenge.answerChoice;
  const expected = [...new Set(challenge.answerPitches || [])].sort((a, b) => a - b);
  const answer = [...new Set(pitches)].sort((a, b) => a - b);
  return (
    expected.length > 0 &&
    expected.length === answer.length &&
    expected.every((pitch, index) => pitch === answer[index])
  );
}
