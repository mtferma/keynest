import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Check from './pages/Check';
import { API_URL } from './config';

// Мокаем Navigation и Footer
jest.mock('./components/Navigation', () => () => <div>Навигация</div>);
jest.mock('./components/Footer', () => () => <div>Футер</div>);

// Мокаем fetch API
global.fetch = jest.fn();

describe('CheckPage', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('отображает CheckPage со всеми элементами', () => {
    render(<Check />);
    expect(screen.getByText('Keynest')).toBeInTheDocument();
    expect(screen.getByText('Запоминающиеся пароли. Безопасно. Просто.')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Введите пароль')).toBeInTheDocument();
    expect(screen.getByText('Проверить')).toBeInTheDocument();
  });

  test('отправляет пароль на проверку и отображает результат', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        strength: 'Надежный',
        time: '100 лет',
        suggestion: null
      })
    });

    render(<Check />);
    const input = screen.getByPlaceholderText('Введите пароль');
    const checkButton = screen.getByText('Проверить');

    fireEvent.change(input, { target: { value: 'lol-ME-KO-ID-ME-KO1949#' } });
    fireEvent.click(checkButton);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(`${API_URL}/check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: 'lol-ME-KO-ID-ME-KO1949#' })
      });
      expect(screen.getByText(/Надежный/i)).toBeInTheDocument();
      expect(screen.getByText(/100 лет/i)).toBeInTheDocument();
    });
  });
});