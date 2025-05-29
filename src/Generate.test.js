import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import GeneratePage from './pages/Generate';
import { API_URL } from './config';

jest.mock('./components/Navigation', () => () => <div>Навигация</div>);
jest.mock('./components/Footer', () => () => <div>Футер</div>);

global.fetch = jest.fn();

describe('GeneratePage', () => {
  beforeEach(() => {
    fetch.mockClear();
    localStorage.clear();
  });

  test('изменяет количество слогов с помощью слайдера', () => {
    render(<GeneratePage />);
    const slider = screen.getByRole('slider');
    fireEvent.change(slider, { target: { value: '4' } });
    fireEvent.mouseUp(slider);
    expect(slider).toHaveValue('4');
  });

  test('генерирует пароль и обновляет localStorage при нажатии кнопки', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        password: 'test-pass-123',
        associations: ['тест', 'пароль', '123']
      })
    });

    render(<GeneratePage />);
    const generateButton = screen.getByText('ГЕНЕРИРОВАТЬ');
    fireEvent.click(generateButton);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(`${API_URL}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          syllables: 5,
          numbers: false,
          symbols: false,
          seed: ''
        })
      });
      expect(screen.getByText('test-pass-123')).toBeInTheDocument();
    });

    const history = JSON.parse(localStorage.getItem('passwordHistory'));
    expect(history).toHaveLength(1);
    expect(history[0].password).toBe('test-pass-123');
  });

  test('копирует пароль в буфер обмена и показывает сообщение', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        password: 'test-pass-123',
        associations: ['тест', 'пароль', '123']
      })
    });

    Object.assign(navigator, {
      clipboard: {
        writeText: jest.fn().mockResolvedValueOnce()
      }
    });

    render(<GeneratePage />);
    const generateButton = screen.getByText('ГЕНЕРИРОВАТЬ');
    const copyButton = screen.getByRole('button', { name: /copy icon/i });

    fireEvent.click(generateButton);

    await waitFor(() => {
      expect(screen.getByText('test-pass-123')).toBeInTheDocument();
    });

    fireEvent.click(copyButton);

    await waitFor(() => {
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith('test-pass-123');
      expect(screen.getByText('Пароль скопирован!')).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.queryByText('Пароль скопирован!')).not.toBeInTheDocument();
    }, { timeout: 3000 });
  });
});